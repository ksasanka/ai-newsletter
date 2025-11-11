"""GitHub Scraper - Scrapes GitHub trending repos"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import logging
import time

logger = logging.getLogger(__name__)


class GitHubScraper:
    """Scraper for GitHub trending repositories"""

    def __init__(self, config: Dict):
        self.config = config
        self.period = config['sources']['github']['trending_period']
        self.languages = config['sources']['github']['languages']
        self.topics = config['sources']['github']['topics']
        self.delay = config['advanced']['request_delay_seconds']
        self.headers = {'User-Agent': 'AI Newsletter Bot 1.0'}

    def scrape_all(self, start_date: datetime) -> List[Dict]:
        """Scrape GitHub trending repositories"""
        all_repos = []

        try:
            logger.info("Scraping GitHub trending...")

            # Scrape trending for each language
            for language in self.languages:
                repos = self.scrape_trending_language(language)
                all_repos.extend(repos)
                time.sleep(self.delay)

            # Scrape by AI topics
            for topic in self.topics:
                repos = self.scrape_topic_repos(topic)
                all_repos.extend(repos)
                time.sleep(self.delay)

            # Deduplicate
            seen_urls = set()
            unique_repos = []
            for repo in all_repos:
                if repo['url'] not in seen_urls:
                    seen_urls.add(repo['url'])
                    unique_repos.append(repo)

            logger.info(f"Total repos from GitHub: {len(unique_repos)}")
            return unique_repos

        except Exception as e:
            logger.error(f"GitHub scraping failed: {e}")
            return []

    def scrape_trending_language(self, language: str) -> List[Dict]:
        """Scrape GitHub trending for a specific language"""
        try:
            url = f"https://github.com/trending/{language}"
            params = {'since': self.period}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            repos = []

            # Find repository articles
            repo_items = soup.find_all('article', class_='Box-row')

            for item in repo_items[:10]:  # Limit to top 10
                try:
                    repo = self._parse_repo_item(item, language)
                    if repo:
                        repos.append(repo)
                except Exception as e:
                    logger.debug(f"Error parsing repo: {e}")
                    continue

            return repos

        except Exception as e:
            logger.error(f"Trending scraping failed for {language}: {e}")
            return []

    def scrape_topic_repos(self, topic: str) -> List[Dict]:
        """Scrape repositories by topic"""
        try:
            url = f"https://github.com/topics/{topic}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            repos = []

            # Find repository articles
            repo_items = soup.find_all('article', class_='border')[:10]

            for item in repo_items:
                try:
                    repo = self._parse_topic_repo_item(item, topic)
                    if repo:
                        repos.append(repo)
                except Exception as e:
                    logger.debug(f"Error parsing repo: {e}")
                    continue

            return repos

        except Exception as e:
            logger.error(f"Topic scraping failed for {topic}: {e}")
            return []

    def _parse_repo_item(self, item, language: str) -> Dict:
        """Parse a trending repository item"""
        # Extract repo name
        h2 = item.find('h2')
        if not h2:
            return None

        link = h2.find('a')
        if not link:
            return None

        repo_name = link.get_text(strip=True).replace(' ', '').replace('\n', '')
        repo_url = 'https://github.com' + link.get('href', '')

        # Extract description
        desc_elem = item.find('p')
        description = desc_elem.get_text(strip=True) if desc_elem else ''

        # Extract stars
        stars_elem = item.find('svg', class_='octicon-star')
        if stars_elem:
            stars_text = stars_elem.find_next('span').get_text(strip=True)
            try:
                stars = int(stars_text.replace(',', ''))
            except:
                stars = 0
        else:
            stars = 0

        # Extract stars today
        stars_today_elem = item.find('span', class_='d-inline-block float-sm-right')
        stars_today = stars_today_elem.get_text(strip=True) if stars_today_elem else '0'

        repo = {
            'title': repo_name,
            'url': repo_url,
            'description': description[:300],
            'source': f'GitHub Trending ({language})',
            'published_date': datetime.now(),  # Approximate
            'type': 'github_repo',
            'stars': stars,
            'stars_today': stars_today,
            'language': language,
            'image_url': None
        }

        return repo

    def _parse_topic_repo_item(self, item, topic: str) -> Dict:
        """Parse a topic repository item"""
        # Extract repo name
        h3 = item.find('h3')
        if not h3:
            return None

        link = h3.find('a')
        if not link:
            return None

        repo_name = link.get_text(strip=True)
        repo_url = 'https://github.com' + link.get('href', '')

        # Extract description
        desc_elem = item.find('p')
        description = desc_elem.get_text(strip=True) if desc_elem else ''

        # Extract stars
        stars_elem = item.find('svg', class_='octicon-star')
        if stars_elem:
            stars_text = stars_elem.find_next().get_text(strip=True)
            try:
                stars = int(stars_text.replace(',', '').replace('k', '000'))
            except:
                stars = 0
        else:
            stars = 0

        repo = {
            'title': repo_name,
            'url': repo_url,
            'description': description[:300],
            'source': f'GitHub Topic ({topic})',
            'published_date': datetime.now(),
            'type': 'github_repo',
            'stars': stars,
            'topic': topic,
            'image_url': None
        }

        return repo
