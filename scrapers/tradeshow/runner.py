
import yaml
import requests
from bs4 import BeautifulSoup
from pathlib import Path

def load_config():
    """
    Load tradeshow configuration (URL and selectors) from config/config.yaml
    """
    project_root = Path(__file__).resolve().parent.parent
    cfg_path = project_root / 'config' / 'config.yaml'
    with open(cfg_path, 'r') as f:
        cfg = yaml.safe_load(f)
    return cfg.get('tradeshows', [])


def run_tradeshow_scraper(show_name: str):
    """
    Given a tradeshow name, find its config and scrape exhibitor names.
    Returns a list of brand/exhibitor names.
    """
    # Load config list
    tradeshows = load_config()
    # Find the matching show
    show_cfg = next((s for s in tradeshows if s['name'] == show_name), None)
    if not show_cfg:
        raise ValueError(f"Tradeshow '{show_name}' not found in configuration.")

    url = show_cfg['url']
    selector = show_cfg.get('selector')  # CSS selector for exhibitor names
    headers = {'User-Agent': show_cfg.get('user_agent', 'Mozilla/5.0')}

    # Fetch page
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    # Parse HTML
    soup = BeautifulSoup(resp.text, 'html.parser')
    exhibitors = []

    if selector:
        elements = soup.select(selector)
        exhibitors = [el.get_text(strip=True) for el in elements]
    else:
        # Fallback: find <h2> or <h3> tags containing names
        headers = soup.find_all(['h2', 'h3'])
        exhibitors = [h.get_text(strip=True) for h in headers]

    # Deduplicate and clean
    seen = set()
    clean_list = []
    for name in exhibitors:
        if name and name not in seen:
            clean_list.append(name)
            seen.add(name)

    return clean_list
