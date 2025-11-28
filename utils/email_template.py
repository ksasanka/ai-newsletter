"""Email Template - Generates HTML email from content"""

from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EmailTemplate:
    """Generate HTML email templates"""

    def __init__(self, config: Dict):
        self.config = config
        self.include_images = config['content']['include_images']

    def generate(self, content: Dict[str, List[Dict]]) -> str:
        """Generate full HTML email"""
        sections_html = []

        # Get category order by priority
        categories = sorted(
            [(name, cfg) for name, cfg in self.config['categories'].items() if cfg['enabled']],
            key=lambda x: x[1]['priority']
        )

        for category_name, category_config in categories:
            items = content.get(category_name, [])
            if not items:
                continue

            section_html = self._generate_section(category_name, items)
            sections_html.append(section_html)

        # Combine all sections
        full_html = self._wrap_in_template('\n'.join(sections_html))

        return full_html

    def _generate_section(self, category: str, items: List[Dict]) -> str:
        """Generate HTML for a category section"""
        # Category title mapping
        titles = {
            'models': '🤖 AI Models & Research',
            'creative_applications': '🎨 Creative Applications',
            'productivity_tools': '⚡ Productivity Tools',
            'product_launches': '🚀 Product Launches'
        }

        title = titles.get(category, category.replace('_', ' ').title())

        items_html = []
        for item in items:
            item_html = self._generate_item(item)
            items_html.append(item_html)

        section_html = f"""
        <div class="section">
            <h2 class="section-title">{title}</h2>
            {''.join(items_html)}
        </div>
        """

        return section_html

    def _generate_item(self, item: Dict) -> str:
        """Generate HTML for a single item"""
        title = item.get('title', 'Untitled')
        url = item.get('url', '#')
        description = item.get('description', '')
        source = item.get('source', '')
        pub_date = item.get('published_date', datetime.now())

        # Format date
        date_str = pub_date.strftime('%b %d, %Y')

        # Build metadata
        metadata_parts = [f'<span class="source">{source}</span>']
        metadata_parts.append(f'<span class="date">{date_str}</span>')

        # Add engagement metrics
        if item.get('upvotes'):
            metadata_parts.append(f'<span class="metric">⬆ {item["upvotes"]}</span>')
        if item.get('score'):
            metadata_parts.append(f'<span class="metric">★ {item["score"]}</span>')
        if item.get('stars'):
            metadata_parts.append(f'<span class="metric">⭐ {item["stars"]}</span>')
        if item.get('comments'):
            metadata_parts.append(f'<span class="metric">💬 {item["comments"]}</span>')

        # Add authors for research papers
        if item.get('authors'):
            metadata_parts.append(f'<span class="authors">{item["authors"]}</span>')

        metadata_html = ' · '.join(metadata_parts)

        # Image
        image_html = ''
        if self.include_images and item.get('image_url'):
            image_url = item['image_url']
            image_html = f'<img src="{image_url}" alt="{title}" class="item-image" />'

        item_html = f"""
        <div class="item">
            {image_html}
            <div class="item-content">
                <h3 class="item-title">
                    <a href="{url}" target="_blank">{title}</a>
                </h3>
                <p class="item-description">{description}</p>
                <div class="item-metadata">{metadata_html}</div>
            </div>
        </div>
        """

        return item_html

    def _wrap_in_template(self, content: str) -> str:
        """Wrap content in full HTML template"""
        date_str = datetime.now().strftime('%B %d, %Y')

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>This Week in AI - {date_str}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}

        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .header {{
            text-align: center;
            border-bottom: 3px solid #4A90E2;
            padding-bottom: 20px;
            margin-bottom: 40px;
        }}

        .header h1 {{
            margin: 0;
            font-size: 32px;
            color: #1a1a1a;
        }}

        .header .subtitle {{
            color: #666;
            font-size: 16px;
            margin-top: 10px;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section-title {{
            font-size: 24px;
            color: #1a1a1a;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}

        .item {{
            margin-bottom: 30px;
            padding-bottom: 30px;
            border-bottom: 1px solid #eee;
        }}

        .item:last-child {{
            border-bottom: none;
        }}

        .item-image {{
            max-width: 200px;
            height: auto;
            float: right;
            margin-left: 20px;
            margin-bottom: 10px;
            border-radius: 4px;
        }}

        .item-content {{
            overflow: hidden;
        }}

        .item-title {{
            margin: 0 0 10px 0;
            font-size: 20px;
        }}

        .item-title a {{
            color: #4A90E2;
            text-decoration: none;
        }}

        .item-title a:hover {{
            text-decoration: underline;
        }}

        .item-description {{
            color: #555;
            margin: 10px 0;
            font-size: 15px;
        }}

        .item-metadata {{
            font-size: 13px;
            color: #888;
            margin-top: 10px;
        }}

        .source {{
            font-weight: 600;
            color: #666;
        }}

        .date {{
            color: #999;
        }}

        .metric {{
            color: #4A90E2;
        }}

        .authors {{
            font-style: italic;
        }}

        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            color: #888;
            font-size: 13px;
        }}

        @media only screen and (max-width: 600px) {{
            body {{
                padding: 10px;
            }}

            .container {{
                padding: 20px;
            }}

            .item-image {{
                float: none;
                max-width: 100%;
                margin: 0 0 10px 0;
            }}

            .header h1 {{
                font-size: 24px;
            }}

            .section-title {{
                font-size: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 This Week in AI</h1>
            <div class="subtitle">Your curated AI digest · {date_str}</div>
        </div>

        {content}

        <div class="footer">
            <p>Generated automatically by This Week in AI</p>
            <p>To modify your preferences, edit <code>config.yaml</code></p>
        </div>
    </div>
</body>
</html>
        """

        return html
