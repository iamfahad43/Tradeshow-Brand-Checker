import yaml
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit


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
    # User selected a tradeshow
    data = request.json
    show = data.get('show')
    # Emit a socket event to client: starting
    socketio.emit('status', {'message': f"Scraping {show} exhibitors..."})

    # 1) Import and run your scraper for the selected show
    from scrapers.tradeshow.runner import run_tradeshow_scraper
    exhibitors = run_tradeshow_scraper(show)
    
    # 2) Emit the count once you have results
    socketio.emit('status', {
        'message': f"Found {len(exhibitors)} exhibitors: {exhibitors[:5]}{'…' if len(exhibitors)>5 else ''}"
    })

    return jsonify({'message': 'Started'}), 202

# ─── SOCKET HANDLERS ───────────────────────────────────────────────────────────
@socketio.on('connect')
def on_connect():
    emit('status', {'message': 'Connected to server.'})

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    socketio.run(app, debug=True)