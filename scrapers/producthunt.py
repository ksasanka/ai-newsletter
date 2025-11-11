"""Product Hunt Scraper - Scrapes Product Hunt for AI products"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import logging
import time

logger = logging.getLogger(__name__)


class ProductHuntScraper:
    """Scraper for Product Hunt"""

    def __init__(self, config: Dict):
        self.config = config
        self.categories = config['sources']['producthunt']['categories']
        self.min_upvotes = config['sources']['producthunt']['min_upvotes']
        self.delay = config['advanced']['request_delay_seconds']
        self.headers = {'User-Agent': 'AI Newsletter Bot 1.0'}

    def scrape_all(self, start_date: datetime) -> List[Dict]:
        """Scrape Product Hunt for AI products"""
        all_products = []

        try:
            logger.info("Scraping Product Hunt...")

            # Scrape main page and topics
            products = self.scrape_main_page()
            all_products.extend(products)

            # Scrape AI topic specifically
            ai_products = self.scrape_topic('ai')
            all_products.extend(ai_products)

            # Deduplicate
            seen_names = set()
            unique_products = []
            for product in all_products:
                if product['title'] not in seen_names:
                    seen_names.add(product['title'])
                    unique_products.append(product)

            logger.info(f"Total products from Product Hunt: {len(unique_products)}")
            return unique_products

        except Exception as e:
            logger.error(f"Product Hunt scraping failed: {e}")
            return []

    def scrape_main_page(self) -> List[Dict]:
        """Scrape Product Hunt main page"""
        try:
            url = "https://www.producthunt.com/"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            products = []

            # Find product cards (adjust selectors as needed)
            product_items = soup.find_all('div', attrs={'data-test': 'post-item'})[:20]

            if not product_items:
                # Fallback selector
                product_items = soup.find_all('article')[:20]

            for item in product_items:
                try:
                    product = self._parse_product_item(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.debug(f"Error parsing product: {e}")
                    continue

            return products

        except Exception as e:
            logger.error(f"Main page scraping failed: {e}")
            return []

    def scrape_topic(self, topic: str) -> List[Dict]:
        """Scrape a specific topic on Product Hunt"""
        try:
            url = f"https://www.producthunt.com/topics/{topic}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            products = []

            # Find product cards
            product_items = soup.find_all('div', attrs={'data-test': 'post-item'})[:20]

            if not product_items:
                product_items = soup.find_all('article')[:20]

            for item in product_items:
                try:
                    product = self._parse_product_item(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.debug(f"Error parsing product: {e}")
                    continue

            return products

        except Exception as e:
            logger.error(f"Topic scraping failed for {topic}: {e}")
            return []

    def _parse_product_item(self, item) -> Dict:
        """Parse a product item element"""
        # Extract title/name
        title_elem = item.find('h3') or item.find('h2')
        if not title_elem:
            title_elem = item.find('a', attrs={'data-test': 'post-name'})

        if not title_elem:
            return None

        title = title_elem.get_text(strip=True)

        # Extract link
        link_elem = item.find('a', href=True)
        url = link_elem['href'] if link_elem else ''
        if url and not url.startswith('http'):
            url = 'https://www.producthunt.com' + url

        # Extract description/tagline
        desc_elem = item.find('p') or item.find(attrs={'data-test': 'post-tagline'})
        description = desc_elem.get_text(strip=True) if desc_elem else ''

        # Extract upvotes
        upvote_elem = item.find(attrs={'data-test': 'vote-button'})
        if upvote_elem:
            upvotes_text = upvote_elem.get_text(strip=True)
            try:
                upvotes = int(''.join(filter(str.isdigit, upvotes_text)))
            except:
                upvotes = 0
        else:
            upvotes = 0

        # Filter by upvotes
        if upvotes < self.min_upvotes:
            return None

        # Extract image
        img_elem = item.find('img')
        image_url = img_elem.get('src') if img_elem else None

        product = {
            'title': title,
            'url': url,
            'description': description[:300],
            'source': 'Product Hunt',
            'published_date': datetime.now(),  # Approximate
            'type': 'product_launch',
            'upvotes': upvotes,
            'image_url': image_url
        }

        return product
