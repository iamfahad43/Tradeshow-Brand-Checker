import yaml
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from scrapers.amazon.checker import check_amazon_presence



# ─── App & Config ─────────────────────────────────────────────────────────────
project_root = Path(__file__).resolve().parent.parent
cfg = yaml.safe_load((project_root / "config/config.yaml").read_text())
app = Flask(__name__)
socketio = SocketIO(app)

# Load tradeshow list from config
tradeshows = cfg.get('tradeshows', [])

# ─── ROUTES ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    # Render dropdown of top tradeshows
    return render_template('index.html', tradeshows=tradeshows)

@app.route('/start', methods=['POST'])
def start_process():
    data = request.json
    show = data.get('show')
    socketio.emit('status', {'message': f"Scraping {show} exhibitors…"})

    # 1) Scrape the exhibitor list
    from scrapers.tradeshow.runner import run_tradeshow_scraper
    exhibitors = run_tradeshow_scraper(show)
    socketio.emit('status', {
      'message': f"Found {len(exhibitors)} exhibitors. Now checking Amazon presence…"
    })

    # 2) For each exhibitor, hit Amazon
    base_url = cfg['amazon']['base_search_url']
    results = []
    for brand in exhibitors:
        socketio.emit('status', {'message': f"Searching Amazon for '{brand}' …"})
        present, urls = check_amazon_presence(brand, base_url)
        results.append({
            'brand':    brand,
            'amazon':   present,
            'products': urls
        })
        socketio.emit('status', {
          'message': f" → {brand}: {'✅' if present else '❌'} ({len(urls)} links)"
        })

    # 3) (Later) you’ll enrich results via SimilarWeb and then send final report…
    socketio.emit('status', {'message': "Amazon checks complete. Now fetching SimilarWeb data…"})

    return jsonify({'message': 'Pipeline started', 'data': results}), 202


# ─── SOCKET HANDLERS ───────────────────────────────────────────────────────────
@socketio.on('connect')
def on_connect():
    emit('status', {'message': 'Connected to server.'})

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    socketio.run(app, debug=True)