# Web Scraping and API Integration
import requests
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_page(self, url):
        """Fetch webpage content"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def parse_links(self, html_content):
        """Extract links from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            full_url = urljoin(self.base_url, link['href'])
            links.append(full_url)
        return links
    
    def scrape_api_data(self, api_endpoint):
        """Scrape data from API"""
        try:
            response = self.session.get(api_endpoint)
            return response.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.error(f"API error: {e}")
            return None

def main():
    scraper = WebScraper("https://httpbin.org")
    
    # Fetch sample data
    html = scraper.fetch_page("https://httpbin.org/html")
    if html:
        links = scraper.parse_links(html)
        logger.info(f"Found {len(links)} links")
    
    # Fetch API data
    api_data = scraper.scrape_api_data("https://httpbin.org/json")
    if api_data:
        logger.info(f"API data: {api_data}")
    
    time.sleep(1)  # Rate limiting

if __name__ == "__main__":
    main()