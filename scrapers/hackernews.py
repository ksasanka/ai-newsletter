"""Hacker News Scraper - Scrapes HN for AI-related stories"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import time

logger = logging.getLogger(__name__)


class HackerNewsScraper:
    """Scraper for Hacker News"""

    def __init__(self, config: Dict):
        self.config = config
        self.min_score = config['sources']['hackernews']['min_score']
        self.keywords = [kw.lower() for kw in config['sources']['hackernews']['keywords']]
        self.delay = config['advanced']['request_delay_seconds']
        self.api_base = "https://hacker-news.firebaseio.com/v0"

    def scrape_all(self, start_date: datetime) -> List[Dict]:
        """Scrape Hacker News top and best stories"""
        all_stories = []

        try:
            logger.info("Scraping Hacker News...")

            # Get top stories
            top_stories = self.scrape_story_list('topstories', start_date, limit=100)
            all_stories.extend(top_stories)

            # Get best stories
            best_stories = self.scrape_story_list('beststories', start_date, limit=100)
            all_stories.extend(best_stories)

            # Deduplicate by ID
            seen_ids = set()
            unique_stories = []
            for story in all_stories:
                if story['hn_id'] not in seen_ids:
                    seen_ids.add(story['hn_id'])
                    unique_stories.append(story)

            logger.info(f"Total stories from Hacker News: {len(unique_stories)}")
            return unique_stories

        except Exception as e:
            logger.error(f"Hacker News scraping failed: {e}")
            return []

    def scrape_story_list(self, list_type: str, start_date: datetime, limit: int = 100) -> List[Dict]:
        """Scrape a specific story list (topstories, beststories, etc.)"""
        try:
            # Get story IDs
            url = f"{self.api_base}/{list_type}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            story_ids = response.json()[:limit]

            stories = []

            for story_id in story_ids:
                try:
                    # Get story details
                    story_url = f"{self.api_base}/item/{story_id}.json"
                    story_response = requests.get(story_url, timeout=10)
                    story_response.raise_for_status()

                    story_data = story_response.json()

                    # Skip if not a story
                    if story_data.get('type') != 'story':
                        continue

                    # Parse timestamp
                    created_time = datetime.fromtimestamp(story_data.get('time', 0))

                    # Filter by date
                    if created_time < start_date:
                        continue

                    # Filter by score
                    score = story_data.get('score', 0)
                    if score < self.min_score:
                        continue

                    # Filter by keywords
                    title = story_data.get('title', '').lower()
                    text = story_data.get('text', '').lower()

                    if not any(keyword in title or keyword in text for keyword in self.keywords):
                        continue

                    story = {
                        'title': story_data.get('title', ''),
                        'url': story_data.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                        'description': story_data.get('text', '')[:300] if story_data.get('text') else '',
                        'source': 'Hacker News',
                        'published_date': created_time,
                        'type': 'hn_story',
                        'score': score,
                        'comments': story_data.get('descendants', 0),
                        'author': story_data.get('by', ''),
                        'hn_id': story_id,
                        'image_url': None
                    }

                    stories.append(story)

                    time.sleep(0.1)  # Rate limiting

                except Exception as e:
                    logger.debug(f"Error fetching story {story_id}: {e}")
                    continue

            return stories

        except Exception as e:
            logger.error(f"Story list scraping failed: {e}")
            return []
