import yaml
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import warnings

# Suppress InsecureRequestWarning when verify=False
from requests.packages.urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

# Use Playwright for dynamic rendering
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def load_config():
    """
    Load tradeshow configuration (URL, selectors, and dynamic flag) from config/config.yaml
    """
    project_root = Path(__file__).resolve().parents[2]
    cfg_path = project_root / 'config' / 'config.yaml'
    with open(cfg_path, 'r') as f:
        cfg = yaml.safe_load(f)
    return cfg.get('tradeshows', [])


def fetch_page_source_dynamic(url: str) -> str:
    """
    Use Playwright to fetch fully-rendered HTML for dynamic pages.
    """
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=30000)
        # Wait for at least one known selector to load
        # You may adjust this selector based on the page
        try:
            page.wait_for_selector('body', timeout=15000)
        except PlaywrightTimeoutError:
            # Timeout; proceed with whatever content is available
            pass
        content = page.content()
        browser.close()
        return content


def run_tradeshow_scraper(show_name: str) -> list[str]:
    """
    Given a tradeshow name, find its config entry and scrape exhibitor names.
    Supports both static and dynamic (JS-rendered) pages.
    """
    # Load all tradeshows
    tradeshows = load_config()
    show_cfg = next((s for s in tradeshows if s['name'] == show_name), None)
    if not show_cfg:
        raise ValueError(f"Tradeshow '{show_name}' not found in configuration.")

    url = show_cfg['url']
    selector = show_cfg.get('selector')
    headers = {'User-Agent': show_cfg.get('user_agent', 'Mozilla/5.0')}
    dynamic = show_cfg.get('dynamic', False)

    # Fetch HTML, using Playwright if dynamic
    if dynamic:
        try:
            html = fetch_page_source_dynamic(url)
        except Exception as e:
            raise RuntimeError(f"Dynamic rendering failed for {url}: {e}")
    else:
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            html = resp.text
        except requests.exceptions.SSLError:
            resp = requests.get(url, headers=headers, timeout=30, verify=False)
            resp.raise_for_status()
            html = resp.text

    soup = BeautifulSoup(html, 'html.parser')
    exhibitors = []

    if selector:
        elements = soup.select(selector)
        exhibitors = [el.get_text(strip=True) for el in elements]
    else:
        # fallback for any headings
        headers_tags = soup.find_all(['h2', 'h3', 'h5'])
        exhibitors = [h.get_text(strip=True) for h in headers_tags]

    # Deduplicate
    seen = set()
    clean_list = []
    for name in exhibitors:
        if name and name not in seen:
            clean_list.append(name)
            seen.add(name)

    return clean_list
