"""Content Filter - Filters, categorizes, and ranks newsletter content"""

from typing import List, Dict
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class ContentFilter:
    """Filter and categorize newsletter content"""

    def __init__(self, config: Dict):
        self.config = config
        self.categories = config['categories']
        self.filtering = config['filtering']

    def categorize_item(self, item: Dict) -> List[str]:
        """Determine which categories an item belongs to"""
        categories = []

        title = item.get('title', '').lower()
        description = item.get('description', '').lower()
        text = f"{title} {description}"

        # Check each category
        for category_name, category_config in self.categories.items():
            if not category_config['enabled']:
                continue

            keywords = [kw.lower() for kw in category_config.get('keywords', [])]

            # Check if any keyword matches
            if any(keyword in text for keyword in keywords):
                categories.append(category_name)

        # If no category matched, try to infer from type
        if not categories:
            item_type = item.get('type', '')
            if 'research' in item_type or 'paper' in item_type:
                categories.append('models')
            elif 'product' in item_type:
                categories.append('product_launches')

        return categories

    def filter_items(self, items: List[Dict], category: str) -> List[Dict]:
        """Filter items for a specific category"""
        filtered = []

        for item in items:
            # Check exclude keywords
            if self._should_exclude(item):
                continue

            # Check engagement requirement
            if self.filtering['require_engagement']:
                if not self._has_engagement(item):
                    continue

            # Check domain trust
            if self.filtering.get('trusted_domains'):
                if not self._is_trusted_domain(item):
                    # Don't completely filter out, just note it
                    item['untrusted_source'] = True

            filtered.append(item)

        return filtered

    def _should_exclude(self, item: Dict) -> bool:
        """Check if item should be excluded"""
        exclude_keywords = self.filtering.get('exclude_keywords', [])
        if not exclude_keywords:
            return False

        title = item.get('title', '').lower()
        description = item.get('description', '').lower()
        text = f"{title} {description}"

        for keyword in exclude_keywords:
            if keyword.lower() in text:
                # Make sure it's not AI-related blockchain/crypto
                if 'ai' not in text and 'machine learning' not in text:
                    return True

        return False

    def _has_engagement(self, item: Dict) -> bool:
        """Check if item has minimum engagement"""
        # Check various engagement metrics, converting to int safely
        def to_int(value):
            """Convert value to int, handling strings and None"""
            if value is None:
                return 0
            if isinstance(value, str):
                # Remove common formatting (commas, k for thousands, etc.)
                value = value.replace(',', '').replace('k', '000').replace('K', '000')
                try:
                    return int(float(value))
                except (ValueError, TypeError):
                    return 0
            try:
                return int(value)
            except (ValueError, TypeError):
                return 0

        upvotes = to_int(item.get('upvotes', 0))
        score = to_int(item.get('score', 0))
        stars = to_int(item.get('stars', 0))
        comments = to_int(item.get('comments', 0))

        # Any significant engagement passes
        return upvotes > 0 or score > 0 or stars > 0 or comments > 0

    def _is_trusted_domain(self, item: Dict) -> bool:
        """Check if item is from a trusted domain"""
        url = item.get('url', '')
        trusted_domains = self.filtering.get('trusted_domains', [])

        if not trusted_domains:
            return True

        for domain in trusted_domains:
            if domain in url:
                return True

        return False

    def deduplicate(self, items: List[Dict]) -> List[Dict]:
        """Remove duplicate items"""
        seen_titles = set()
        unique_items = []

        for item in items:
            # Normalize title
            title = item.get('title', '').lower().strip()
            title = re.sub(r'\s+', ' ', title)  # Normalize whitespace

            # Check for very similar titles
            is_duplicate = False
            for seen_title in seen_titles:
                if self._similarity(title, seen_title) > 0.85:
                    is_duplicate = True
                    break

            if not is_duplicate:
                seen_titles.add(title)
                unique_items.append(item)

        logger.info(f"Deduplicated: {len(items)} -> {len(unique_items)} items")
        return unique_items

    def _similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity between two strings"""
        # Simple word-based similarity
        words1 = set(s1.split())
        words2 = set(s2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def rank_items(self, items: List[Dict], category: str) -> List[Dict]:
        """Rank items by relevance and quality"""
        # Calculate score for each item
        for item in items:
            score = self._calculate_score(item, category)
            item['_ranking_score'] = score

        # Sort by score
        ranked = sorted(items, key=lambda x: x.get('_ranking_score', 0), reverse=True)

        return ranked

    def _calculate_score(self, item: Dict, category: str) -> float:
        """Calculate relevance score for an item"""
        def to_int(value):
            """Convert value to int, handling strings and None"""
            if value is None:
                return 0
            if isinstance(value, str):
                # Remove common formatting (commas, k for thousands, etc.)
                value = value.replace(',', '').replace('k', '000').replace('K', '000')
                try:
                    return int(float(value))
                except (ValueError, TypeError):
                    return 0
            try:
                return int(value)
            except (ValueError, TypeError):
                return 0

        score = 0.0

        # Priority boost from category config
        category_config = self.categories.get(category, {})
        priority = category_config.get('priority', 5)
        score += (6 - priority) * 10  # Higher priority = higher score

        # Recency boost (newer is better)
        pub_date = item.get('published_date')
        if pub_date:
            days_old = (datetime.now() - pub_date).days
            if days_old == 0:
                score += 20
            elif days_old == 1:
                score += 15
            elif days_old == 2:
                score += 10
            elif days_old == 3:
                score += 5

        # Engagement boost (convert to int safely)
        upvotes = to_int(item.get('upvotes', 0))
        score += min(upvotes / 10, 20)  # Max 20 points

        score_metric = to_int(item.get('score', 0))
        score += min(score_metric / 10, 20)

        stars = to_int(item.get('stars', 0))
        score += min(stars / 100, 20)

        comments = to_int(item.get('comments', 0))
        score += min(comments / 5, 10)

        # Source boost (trusted sources get higher score)
        if not item.get('untrusted_source', False):
            score += 10

        # Type boost
        item_type = item.get('type', '')
        if 'research' in item_type or 'paper' in item_type:
            score += 5  # Research papers are valuable

        if item.get('has_code', False):
            score += 5  # Code availability is valuable

        return score
