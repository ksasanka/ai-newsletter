#!/usr/bin/env python3
"""
AI Newsletter Generator
Scrapes multiple sources for AI news and sends a curated newsletter
"""

import os
import sys
import yaml
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import List, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import pytz

# Import scrapers
from scrapers.company_blogs import CompanyBlogScraper
from scrapers.research import ResearchScraper
from scrapers.reddit_scraper import RedditScraper
from scrapers.hackernews import HackerNewsScraper
from scrapers.producthunt import ProductHuntScraper
from scrapers.github_scraper import GitHubScraper
from utils.content_filter import ContentFilter
from utils.email_template import EmailTemplate

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('newsletter.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AINewsletterGenerator:
    """Main class for generating AI newsletters"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the newsletter generator"""
        self.config = self.load_config(config_path)
        self.setup_cache()
        self.content_filter = ContentFilter(self.config)
        self.email_template = EmailTemplate(self.config)

    def load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)

    def setup_cache(self):
        """Setup cache directory"""
        cache_dir = self.config['advanced']['cache_directory']
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"Cache directory: {cache_dir}")

    def collect_content(self) -> Dict[str, List[Dict]]:
        """Collect content from all enabled sources"""
        logger.info("Starting content collection...")

        all_content = {
            'models': [],
            'creative_applications': [],
            'productivity_tools': [],
            'product_launches': []
        }

        # Get date range
        days_back = self.config['content']['days_to_look_back']
        start_date = datetime.now() - timedelta(days=days_back)

        # Collect from company blogs
        if self.config['sources']['company_blogs']['enabled']:
            logger.info("Scraping company blogs...")
            blog_scraper = CompanyBlogScraper(self.config)
            blog_content = blog_scraper.scrape_all(start_date)
            self._categorize_content(blog_content, all_content)

        # Collect from research sources
        if self.config['sources']['research']['enabled']:
            logger.info("Scraping research sources...")
            research_scraper = ResearchScraper(self.config)
            research_content = research_scraper.scrape_all(start_date)
            self._categorize_content(research_content, all_content)

        # Collect from Reddit
        if self.config['sources']['reddit']['enabled']:
            logger.info("Scraping Reddit...")
            reddit_scraper = RedditScraper(self.config)
            reddit_content = reddit_scraper.scrape_all(start_date)
            self._categorize_content(reddit_content, all_content)

        # Collect from Hacker News
        if self.config['sources']['hackernews']['enabled']:
            logger.info("Scraping Hacker News...")
            hn_scraper = HackerNewsScraper(self.config)
            hn_content = hn_scraper.scrape_all(start_date)
            self._categorize_content(hn_content, all_content)

        # Collect from Product Hunt
        if self.config['sources']['producthunt']['enabled']:
            logger.info("Scraping Product Hunt...")
            ph_scraper = ProductHuntScraper(self.config)
            ph_content = ph_scraper.scrape_all(start_date)
            self._categorize_content(ph_content, all_content)

        # Collect from GitHub
        if self.config['sources']['github']['enabled']:
            logger.info("Scraping GitHub...")
            github_scraper = GitHubScraper(self.config)
            github_content = github_scraper.scrape_all(start_date)
            self._categorize_content(github_content, all_content)

        logger.info("Content collection complete")
        return all_content

    def _categorize_content(self, items: List[Dict], all_content: Dict):
        """Categorize items into appropriate categories"""
        for item in items:
            # Check which categories this item belongs to
            categories = self.content_filter.categorize_item(item)
            for category in categories:
                if category in all_content:
                    all_content[category].append(item)

    def filter_and_rank_content(self, all_content: Dict) -> Dict[str, List[Dict]]:
        """Filter and rank content for each category"""
        logger.info("Filtering and ranking content...")

        filtered_content = {}

        for category, items in all_content.items():
            if not self.config['categories'][category]['enabled']:
                continue

            # Filter items
            filtered_items = self.content_filter.filter_items(items, category)

            # Deduplicate
            if self.config['filtering']['deduplicate']:
                filtered_items = self.content_filter.deduplicate(filtered_items)

            # Rank by relevance/quality
            ranked_items = self.content_filter.rank_items(filtered_items, category)

            # Limit to configured max
            max_items = self.config['content']['max_items_per_category']
            filtered_content[category] = ranked_items[:max_items]

            logger.info(f"{category}: {len(filtered_content[category])} items")

        return filtered_content

    def generate_email(self, content: Dict) -> str:
        """Generate HTML email from content"""
        logger.info("Generating email...")
        return self.email_template.generate(content)

    def send_email(self, html_content: str):
        """Send email via Gmail SMTP"""
        logger.info("Sending email...")

        email_config = self.config['email']

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"{email_config['subject_prefix']} - {datetime.now().strftime('%B %d, %Y')}"
        msg['From'] = f"{email_config['sender_name']} <{email_config['sender']}>"
        msg['To'] = email_config['recipient']

        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        # Send via SMTP
        try:
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['sender'], email_config['smtp_password'])
                server.send_message(msg)
            logger.info(f"Email sent successfully to {email_config['recipient']}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise

    def run(self):
        """Main execution method"""
        logger.info("=" * 50)
        logger.info("AI Newsletter Generator Started")
        logger.info("=" * 50)

        try:
            # Collect content
            all_content = self.collect_content()

            # Filter and rank
            filtered_content = self.filter_and_rank_content(all_content)

            # Check if we have enough content
            total_items = sum(len(items) for items in filtered_content.values())
            logger.info(f"Total items in newsletter: {total_items}")

            if total_items == 0:
                logger.warning("No content found for newsletter")
                return

            # Generate email
            html_content = self.generate_email(filtered_content)

            # Save to file for preview (optional)
            if self.config['advanced']['debug_mode']:
                with open('newsletter_preview.html', 'w') as f:
                    f.write(html_content)
                logger.info("Preview saved to newsletter_preview.html")

            # Send email
            self.send_email(html_content)

            logger.info("Newsletter generation complete!")

        except Exception as e:
            logger.error(f"Newsletter generation failed: {e}", exc_info=True)
            raise


def main():
    """Entry point"""
    generator = AINewsletterGenerator()
    generator.run()


if __name__ == "__main__":
    main()
