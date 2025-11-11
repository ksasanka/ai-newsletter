"""Research Scraper - Scrapes arXiv, Papers with Code, Hugging Face Papers"""

import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import logging
import time

logger = logging.getLogger(__name__)


class ResearchScraper:
    """Scraper for research papers and academic sources"""

    def __init__(self, config: Dict):
        self.config = config
        self.sources = config['sources']['research']['sources']
        self.delay = config['advanced']['request_delay_seconds']

    def scrape_all(self, start_date: datetime) -> List[Dict]:
        """Scrape all research sources"""
        all_papers = []

        for source in self.sources:
            try:
                if source['name'] == 'arXiv AI':
                    papers = self.scrape_arxiv(source, start_date)
                elif source['name'] == 'Papers with Code':
                    papers = self.scrape_papers_with_code(start_date)
                elif source['name'] == 'Hugging Face Papers':
                    papers = self.scrape_huggingface_papers(start_date)
                else:
                    papers = []

                all_papers.extend(papers)
                time.sleep(self.delay)

            except Exception as e:
                logger.error(f"Error scraping {source['name']}: {e}")

        logger.info(f"Total papers from research sources: {len(all_papers)}")
        return all_papers

    def scrape_arxiv(self, source: Dict, start_date: datetime) -> List[Dict]:
        """Scrape arXiv for AI papers"""
        try:
            # arXiv API endpoint
            base_url = "http://export.arxiv.org/api/query"
            query = source['query']
            max_results = source['max_results']

            # Build query
            params = {
                'search_query': query,
                'start': 0,
                'max_results': max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }

            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()

            feed = feedparser.parse(response.content)
            papers = []

            for entry in feed.entries:
                # Parse date
                pub_date = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ')

                # Filter by date
                if pub_date < start_date:
                    continue

                # Extract authors
                authors = [author.name for author in entry.authors[:3]]  # First 3 authors
                if len(entry.authors) > 3:
                    authors.append('et al.')

                paper = {
                    'title': entry.title.replace('\n', ' ').strip(),
                    'url': entry.link,
                    'description': entry.summary.replace('\n', ' ').strip()[:300],
                    'source': 'arXiv',
                    'published_date': pub_date,
                    'type': 'research_paper',
                    'authors': ', '.join(authors),
                    'arxiv_id': entry.id.split('/')[-1],
                    'image_url': None  # arXiv doesn't provide images
                }

                papers.append(paper)

            logger.info(f"Found {len(papers)} papers from arXiv")
            return papers

        except Exception as e:
            logger.error(f"arXiv scraping failed: {e}")
            return []

    def scrape_papers_with_code(self, start_date: datetime) -> List[Dict]:
        """Scrape Papers with Code for recent papers"""
        try:
            url = "https://paperswithcode.com/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            papers = []

            # Find paper cards (adjust selectors based on current site structure)
            paper_items = soup.find_all('div', class_='paper-card')[:20]

            for item in paper_items:
                try:
                    title_elem = item.find('h1') or item.find('a')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = 'https://paperswithcode.com' + link

                    # Extract description
                    desc_elem = item.find('p', class_='item-strip-abstract')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''

                    # Extract code availability
                    code_elem = item.find('a', string=lambda text: text and 'code' in text.lower())
                    has_code = code_elem is not None

                    paper = {
                        'title': title,
                        'url': link,
                        'description': description[:300],
                        'source': 'Papers with Code',
                        'published_date': datetime.now(),  # Approximate
                        'type': 'research_paper',
                        'has_code': has_code,
                        'image_url': None
                    }

                    papers.append(paper)

                except Exception as e:
                    logger.debug(f"Error parsing paper: {e}")
                    continue

            logger.info(f"Found {len(papers)} papers from Papers with Code")
            return papers

        except Exception as e:
            logger.error(f"Papers with Code scraping failed: {e}")
            return []

    def scrape_huggingface_papers(self, start_date: datetime) -> List[Dict]:
        """Scrape Hugging Face daily papers"""
        try:
            url = "https://huggingface.co/papers"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            papers = []

            # Find paper articles
            paper_items = soup.find_all('article')[:20]

            for item in paper_items:
                try:
                    # Extract title
                    title_elem = item.find('h3') or item.find('h2')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)

                    # Extract link
                    link_elem = item.find('a', href=True)
                    link = link_elem['href'] if link_elem else ''
                    if link and not link.startswith('http'):
                        link = 'https://huggingface.co' + link

                    # Extract description/abstract
                    desc_elem = item.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''

                    # Extract upvotes/likes
                    upvotes_elem = item.find('span', string=lambda text: text and '↑' in text)
                    upvotes = upvotes_elem.get_text(strip=True) if upvotes_elem else '0'

                    paper = {
                        'title': title,
                        'url': link,
                        'description': description[:300],
                        'source': 'Hugging Face Papers',
                        'published_date': datetime.now(),  # Approximate
                        'type': 'research_paper',
                        'upvotes': upvotes,
                        'image_url': None
                    }

                    papers.append(paper)

                except Exception as e:
                    logger.debug(f"Error parsing paper: {e}")
                    continue

            logger.info(f"Found {len(papers)} papers from Hugging Face")
            return papers

        except Exception as e:
            logger.error(f"Hugging Face papers scraping failed: {e}")
            return []
