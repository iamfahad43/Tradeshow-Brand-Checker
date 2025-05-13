# scrapers/amazon/checker.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from pathlib import Path
import time

def init_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(30)
    return driver

def check_amazon_presence(brand: str, base_url: str, max_products=5):
    """
    Search Amazon for the brand name.
    Returns:
      - present: bool
      - product_urls: list[str] (up to max_products)
    """
    driver = init_driver(headless=True)
    try:
        search_url = base_url + brand.replace(" ", "+")
        driver.get(search_url)
        time.sleep(2)  # wait for page to load JS

        # CSS selector for each result item
        items = driver.find_elements_by_css_selector("div.s-main-slot div[data-component-type='s-search-result'] a.a-link-normal")
        product_urls = []
        for item in items[:max_products]:
            href = item.get_attribute("href")
            product_urls.append(href)

        present = len(product_urls) > 0
        return present, product_urls

    except TimeoutException:
        return False, []
    finally:
        driver.quit()
