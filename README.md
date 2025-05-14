# Tradeshow Brand Checker Web App

An interactive web application that automates the process of:

1. Scraping exhibitor/brand names from major trade-show websites (static & JS-driven)
2. Checking product presence on Amazon via headless browser automation
3. Enriching each brand with traffic & revenue data from SimilarWeb (via API)
4. Streaming live progress updates in the browser
5. Exporting final results as CSV or Excel

Built with Flask, Socket.IO, Playwright, and Selenium.

---

## 🚀 Features

* **Multi-Source Scraping**: Supports both static (requests & BeautifulSoup) and dynamic (Playwright) pages.
* **Real-Time UI**: Live progress log via Socket.IO—users see each step as it happens.
* **Amazon Presence**: Headless browser searches for each brand and captures sample product links.
* **Config-Driven**: Easily swap in new trade shows or adjust CSS selectors in a single YAML file.
* **Extensible Pipeline**: Modular scrapers for trade shows, Amazon, and SimilarWeb—simple to add new stages.
* **Export**: Download enriched data as CSV or Excel for further analysis.

---

## 🛠️ Tech Stack

* **Backend**: Flask & Flask-SocketIO
* **Dynamic Rendering**: Playwright (Chromium)
* **Static Scraping**: requests & BeautifulSoup
* **Browser Automation**: Selenium (Amazon checks)
* **Configuration**: YAML-driven
* **Database**: SQLite (via SQLAlchemy) or CSV/Excel output
* **Frontend**: Jinja2 templates + vanilla JavaScript

---

## 📦 Installation

1. **Clone the repo**

   ```bash
   git clone https://github.com/iamfahad43/tradeshow-brand-checker.git
   cd tradeshow-brand-checker
   ```

2. **Create a Python virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

4. **Configure**

   * Copy `config/config.example.yaml` → `config/config.yaml`
   * Fill in your target trade shows, selectors, and SimilarWeb API key.

---

## ⚙️ Configuration (`config/config.yaml`)

```yaml
tradeshows:
  - name: MWC Barcelona
    url: https://www.mwcbarcelona.com/exhibitors
    selector: "h3 span.ais-Highlight-nonHighlighted"
    dynamic: true

  - name: IFA Berlin
    url: https://b2b.ifa-berlin.com/exhibitors
    selector: "div.exhibitor-card-wrapper h2"

  - name: NRF Big Show
    url: https://nrfbigshow.nrf.com/exhibitors
    selector: "div h5"

amazon:
  base_search_url: https://www.amazon.com/s?k=
similarweb:
  api_key: YOUR_SIMILARWEB_API_KEY
database:
  dialect: sqlite
  filename: data/brands.db
```

* **`dynamic: true`** tells the scraper to use Playwright for JS-rendered pages.
* **`selector`** is a CSS selector that pinpoints the exhibitor name element.

---

## 🚀 Running the App

1. **Start the Flask server**

   ```bash
   export FLASK_APP=app/main.py
   flask run
   ```

2. **Open** [http://localhost:5000](http://localhost:5000) in your browser.

3. **Select** a trade show from the dropdown and click **Start**.

4. **Watch** live updates as exhibitors are scraped, Amazon checks run, and SimilarWeb data is fetched.

5. **Download** the final report when complete.

---

## 🔧 Project Structure

```
├── app/
│   ├── main.py           # Flask + Socket.IO entrypoint
│   └── templates/
│       └── index.html    # UI with dropdown & live log
├── config/
│   └── config.yaml       # Trade-show list, selectors, API keys
├── scrapers/
│   ├── tradeshow/        # trade-show scraper module (static & dynamic)
│   └── amazon/           # Amazon presence checker
├── requirements.txt      # Python dependencies
├── scripts/              # (optional) export helpers, CLI runners
├── data/                 # SQLite DB or raw cache (gitignored)
├── output/               # CSV/Excel exports
└── README.md             # This file
```

---

## 🤝 Contribution

Contributions, issues, and feature requests are welcome! Feel free to open a discussion or pull request.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
