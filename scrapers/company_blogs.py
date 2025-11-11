"""Company Blog Scraper - Scrapes AI company blogs and news pages"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import logging
import time

logger = logging.getLogger(__name__)


class CompanyBlogScraper:
    """Scraper for company blogs and news pages"""

    def __init__(self, config: Dict):
        self.config = config
        self.blogs = config['sources']['company_blogs']['urls']
        self.delay = config['advanced']['request_delay_seconds']

    def scrape_all(self, start_date: datetime) -> List[Dict]:
        """Scrape all configured company blogs"""
        all_posts = []

        for blog in self.blogs:
            try:
                logger.info(f"Scraping {blog['name']}...")
                posts = self.scrape_blog(blog, start_date)
                all_posts.extend(posts)
                time.sleep(self.delay)
            except Exception as e:
                logger.error(f"Error scraping {blog['name']}: {e}")

        logger.info(f"Total posts from company blogs: {len(all_posts)}")
        return all_posts

    def scrape_blog(self, blog: Dict, start_date: datetime) -> List[Dict]:
        """Scrape a single blog"""
        posts = []

        # Try RSS feed first
        if 'rss' in blog and blog['rss']:
            posts = self._scrape_rss(blog, start_date)

        # Fallback to web scraping if RSS fails or not available
        if not posts:
            posts = self._scrape_web(blog, start_date)

        return posts

    def _scrape_rss(self, blog: Dict, start_date: datetime) -> List[Dict]:
        """Scrape blog via RSS feed"""
        try:
            feed = feedparser.parse(blog['rss'])
            posts = []

            for entry in feed.entries:
                # Parse date
                if hasattr(entry, 'published_parsed'):
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed'):
                    pub_date = datetime(*entry.updated_parsed[:6])
                else:
                    pub_date = datetime.now()

                # Filter by date
                if pub_date < start_date:
                    continue

                # Extract content
                description = entry.get('summary', entry.get('description', ''))

                post = {
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'description': description,
                    'source': blog['name'],
                    'published_date': pub_date,
                    'type': 'blog_post',
                    'image_url': self._extract_image(entry)
                }

                posts.append(post)

            return posts

        except Exception as e:
            logger.error(f"RSS scraping failed for {blog['name']}: {e}")
            return []

    def _scrape_web(self, blog: Dict, start_date: datetime) -> List[Dict]:
        """Scrape blog via web scraping"""
        try:
            response = requests.get(blog['url'], timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Generic selectors (customize per site as needed)
            posts = []

            # Find article/blog post elements
            articles = soup.find_all(['article', 'div'], class_=lambda x: x and ('post' in x.lower() or 'article' in x.lower()))

            for article in articles[:10]:  # Limit to recent 10
                try:
                    # Extract title
                    title_elem = article.find(['h1', 'h2', 'h3'])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)

                    # Extract link
                    link_elem = article.find('a', href=True)
                    if not link_elem:
                        continue
                    url = link_elem['href']
                    if not url.startswith('http'):
                        url = blog['url'].rstrip('/') + '/' + url.lstrip('/')

                    # Extract description
                    desc_elem = article.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''

                    # Extract image
                    img_elem = article.find('img')
                    image_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else None

                    post = {
                        'title': title,
                        'url': url,
                        'description': description[:300],  # Limit description
                        'source': blog['name'],
                        'published_date': datetime.now(),  # Approximate
                        'type': 'blog_post',
                        'image_url': image_url
                    }

                    posts.append(post)

                except Exception as e:
                    logger.debug(f"Error parsing article: {e}")
                    continue

            return posts

        except Exception as e:
            logger.error(f"Web scraping failed for {blog['name']}: {e}")
            return []

    def _extract_image(self, entry) -> str:
        """Extract image from RSS entry"""
        # Try media:content
        if hasattr(entry, 'media_content'):
            for media in entry.media_content:
                if media.get('medium') == 'image':
                    return media.get('url')

        # Try media:thumbnail
        if hasattr(entry, 'media_thumbnail'):
            return entry.media_thumbnail[0]['url']

        # Try enclosure
        if hasattr(entry, 'enclosures'):
            for enclosure in entry.enclosures:
                if 'image' in enclosure.get('type', ''):
                    return enclosure.get('href')

        # Try parsing from content
        if hasattr(entry, 'content'):
            soup = BeautifulSoup(entry.content[0].value, 'html.parser')
            img = soup.find('img')
            if img and img.get('src'):
                return img['src']

        return None
