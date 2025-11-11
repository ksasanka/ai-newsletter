"""Reddit Scraper - Scrapes AI-related subreddits"""

import requests
from datetime import datetime
from typing import List, Dict
import logging
import time

logger = logging.getLogger(__name__)


class RedditScraper:
    """Scraper for Reddit submissions"""

    def __init__(self, config: Dict):
        self.config = config
        self.subreddits = config['sources']['reddit']['subreddits']
        self.min_upvotes = config['sources']['reddit']['min_upvotes']
        self.delay = config['advanced']['request_delay_seconds']
        self.headers = {'User-Agent': 'AI Newsletter Bot 1.0'}

    def scrape_all(self, start_date: datetime) -> List[Dict]:
        """Scrape all configured subreddits"""
        all_posts = []

        for subreddit in self.subreddits:
            try:
                logger.info(f"Scraping r/{subreddit}...")
                posts = self.scrape_subreddit(subreddit, start_date)
                all_posts.extend(posts)
                time.sleep(self.delay)
            except Exception as e:
                logger.error(f"Error scraping r/{subreddit}: {e}")

        logger.info(f"Total posts from Reddit: {len(all_posts)}")
        return all_posts

    def scrape_subreddit(self, subreddit: str, start_date: datetime) -> List[Dict]:
        """Scrape a single subreddit"""
        try:
            # Use Reddit's JSON API (no authentication needed for public subs)
            url = f"https://www.reddit.com/r/{subreddit}/hot.json"
            params = {'limit': 50}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            posts = []

            for post_data in data['data']['children']:
                post = post_data['data']

                # Filter by upvotes
                if post.get('ups', 0) < self.min_upvotes:
                    continue

                # Parse timestamp
                created_time = datetime.fromtimestamp(post.get('created_utc', 0))

                # Filter by date
                if created_time < start_date:
                    continue

                # Extract image
                image_url = None
                if post.get('thumbnail') and post['thumbnail'].startswith('http'):
                    image_url = post['thumbnail']
                elif post.get('url') and any(post['url'].endswith(ext) for ext in ['.jpg', '.png', '.gif']):
                    image_url = post['url']

                item = {
                    'title': post.get('title', ''),
                    'url': f"https://www.reddit.com{post.get('permalink', '')}",
                    'description': post.get('selftext', '')[:300],
                    'source': f"r/{subreddit}",
                    'published_date': created_time,
                    'type': 'reddit_post',
                    'upvotes': post.get('ups', 0),
                    'comments': post.get('num_comments', 0),
                    'author': post.get('author', ''),
                    'image_url': image_url
                }

                posts.append(item)

            return posts

        except Exception as e:
            logger.error(f"Subreddit scraping failed for r/{subreddit}: {e}")
            return []
