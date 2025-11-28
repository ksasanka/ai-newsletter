# This Week in AI

An automated newsletter system that curates AI news from multiple sources and delivers a beautiful HTML email digest.

## Quick Start (GitHub Clone)

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-newsletter.git
cd ai-newsletter

# Install dependencies
pip3 install -r requirements.txt

# Copy sample config and customize
cp config.sample.yaml config.yaml
# Edit config.yaml with your email and Gmail App Password

# Test run
python3 newsletter.py

# Set up automated schedule (optional)
chmod +x setup_cron.sh
./setup_cron.sh
```

## Features

- **Multi-Source Aggregation**: Scrapes content from:
  - Company blogs (OpenAI, Anthropic, Google, Meta, Mistral, etc.)
  - Research papers (arXiv, Papers with Code, Hugging Face)
  - Social media (Reddit, Hacker News)
  - Product launches (Product Hunt)
  - GitHub trending repositories

- **Smart Categorization**:
  - AI Models & Research
  - Creative Applications
  - Productivity Tools
  - Product Launches

- **Fully Configurable**: Every aspect is customizable via `config.yaml`
  - Sources and keywords
  - Email schedule and formatting
  - Content filters and thresholds
  - Categories and priorities

- **Beautiful HTML Emails**: Responsive design that looks great on all devices

## Detailed Setup Instructions

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-newsletter.git
cd ai-newsletter

# Install dependencies
pip3 install -r requirements.txt
```

### 2. Create Your Configuration

```bash
# Copy the sample configuration
cp config.sample.yaml config.yaml
```

### 3. Configure Gmail App Password

To send emails via Gmail, you need to create an App Password:

1. Go to your Google Account settings: https://myaccount.google.com/
2. Select **Security** from the left menu
3. Under "Signing in to Google," select **2-Step Verification** (you must have this enabled)
4. Scroll to the bottom and select **App passwords**
5. Select **Mail** and **Mac** as the app and device
6. Click **Generate**
7. Copy the 16-character password (it will look like: `xxxx xxxx xxxx xxxx`)

### 4. Update Configuration

Edit `config.yaml` and add your email and Gmail App Password:

```yaml
email:
  recipient: "your-email@gmail.com"
  sender: "your-email@gmail.com"
  smtp_password: "YOUR_APP_PASSWORD_HERE"  # Paste the 16-character password
```

### 5. Customize Your Preferences

Edit `config.yaml` to customize:

- **Sources**: Enable/disable specific sources
- **Keywords**: Add or remove keywords for each category
- **Schedule**: Set days and times for delivery
- **Content limits**: Adjust min/max items per category
- **Filters**: Add exclude keywords or trusted domains

### 6. Test the Newsletter

Run a test to make sure everything works:

```bash
python3 newsletter.py
```

Check:
1. The script runs without errors
2. You receive an email
3. The email looks good and contains content

If debug mode is enabled in config, you'll also see a `newsletter_preview.html` file.

### 7. Schedule with Cron (Optional)

The easiest way is to use the provided setup script:

```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

Or manually add to cron:

```bash
# Open cron editor
crontab -e
```

Add this line (replace `/path/to/ai-newsletter` with actual path):

```cron
# AI Newsletter - Mondays and Thursdays at 8 AM
0 8 * * 1,4 cd /path/to/ai-newsletter && /usr/bin/python3 newsletter.py >> /path/to/ai-newsletter/cron.log 2>&1
```

### 8. Verify Cron Setup

Check your cron jobs:

```bash
crontab -l
```

You should see your AI Newsletter entry.

## Configuration Guide

### Email Settings

```yaml
email:
  recipient: "your-email@gmail.com"
  sender: "your-email@gmail.com"
  sender_name: "AI Newsletter"
  subject_prefix: "AI Weekly Digest"
  smtp_password: "your-app-password"
```

### Schedule Settings

```yaml
schedule:
  days: ["Monday", "Thursday"]  # Days to send
  time: "08:00"  # Time in 24-hour format
  timezone: "America/Los_Angeles"
```

### Content Settings

```yaml
content:
  days_to_look_back: 4  # How many days of content to include
  min_items_per_category: 5
  max_items_per_category: 10
  include_images: true
```

### Adding/Removing Sources

To add a new company blog:

```yaml
sources:
  company_blogs:
    urls:
      - url: "https://example.com/blog"
        name: "Example Blog"
        rss: "https://example.com/feed.xml"  # Optional
```

To disable a source:

```yaml
sources:
  reddit:
    enabled: false  # Disables Reddit scraping
```

### Customizing Categories

Add keywords to existing categories:

```yaml
categories:
  models:
    keywords:
      - "GPT"
      - "LLM"
      - "your-custom-keyword"
```

### Filtering Content

Exclude certain topics:

```yaml
filtering:
  exclude_keywords:
    - "crypto"
    - "NFT"
    - "your-excluded-topic"
```

## Troubleshooting

### Email Not Sending

1. **Check App Password**: Make sure you copied the full 16-character password
2. **Check 2FA**: Gmail App Passwords require 2-Step Verification to be enabled
3. **Check Logs**: Look at `newsletter.log` for error messages
4. **Test SMTP**: Try a simpler test:

```python
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
print("Success!")
server.quit()
```

### No Content in Newsletter

1. **Check Date Range**: Increase `days_to_look_back` in config
2. **Check Keywords**: Make sure keywords aren't too restrictive
3. **Check Min Upvotes**: Lower `min_upvotes` thresholds
4. **Enable Debug Mode**: Set `debug_mode: true` in config to see detailed logs

### Scraping Errors

Some websites may block scrapers or change their HTML structure:

1. **Check Logs**: Look for specific error messages
2. **Test Individual Sources**: Comment out sources in config to isolate issues
3. **Update Selectors**: Website structures change; you may need to update scraper code

### Cron Not Running

1. **Check Cron Logs**:
```bash
tail -f cron.log
```

2. **Check Cron Service** (Mac):
```bash
# Cron should be running
ps aux | grep cron
```

3. **Full Paths**: Make sure cron job uses full absolute paths:
```cron
0 8 * * 1,4 cd /full/path/to/ai-newsletter && /usr/bin/python3 newsletter.py
```

4. **Permissions**: Make sure the script has execute permissions:
```bash
chmod +x newsletter.py
```

## File Structure

```
ai-newsletter/
├── .gitignore              # Git ignore file
├── LICENSE                 # MIT License
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── config.sample.yaml      # Sample configuration (copy to config.yaml)
├── config.yaml             # Your configuration (not in git)
├── newsletter.py           # Main script
├── setup_cron.sh          # Cron setup script
├── scrapers/              # Source scrapers
│   ├── __init__.py
│   ├── company_blogs.py
│   ├── research.py
│   ├── reddit_scraper.py
│   ├── hackernews.py
│   ├── producthunt.py
│   └── github_scraper.py
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── content_filter.py
│   └── email_template.py
├── cache/                 # Cache directory (auto-created, not in git)
├── newsletter.log         # Application logs (not in git)
└── cron.log              # Cron execution logs (not in git)
```

## Advanced Customization

### Adding a New Source

1. Create a new scraper in `scrapers/`:

```python
# scrapers/my_source.py
class MySourceScraper:
    def __init__(self, config):
        self.config = config

    def scrape_all(self, start_date):
        # Your scraping logic
        return items
```

2. Import and use in `newsletter.py`:

```python
from scrapers.my_source import MySourceScraper

# In collect_content method:
if self.config['sources']['my_source']['enabled']:
    scraper = MySourceScraper(self.config)
    content = scraper.scrape_all(start_date)
    self._categorize_content(content, all_content)
```

3. Add config section in `config.yaml`:

```yaml
sources:
  my_source:
    enabled: true
    # Your custom settings
```

### Customizing Email Template

Edit `utils/email_template.py` to modify the HTML/CSS:

- Change colors in the `<style>` section
- Modify section headers
- Adjust layout and spacing
- Add custom branding

### Adding New Categories

1. Add to `config.yaml`:

```yaml
categories:
  my_category:
    enabled: true
    priority: 5
    keywords:
      - "keyword1"
      - "keyword2"
```

2. Add section title in `utils/email_template.py`:

```python
titles = {
    # ... existing ...
    'my_category': '🔥 My Category Name'
}
```

## Tips for Best Results

1. **Start Broad**: Begin with more sources and keywords, then narrow down
2. **Monitor Quality**: Check first few newsletters and adjust filters
3. **Adjust Thresholds**: Lower min_upvotes if you're getting too little content
4. **Review Regularly**: AI news changes fast; review config monthly
5. **Check Logs**: Keep an eye on `newsletter.log` for any issues

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in `newsletter.log`
3. Enable debug mode for more details
4. Check individual scraper source code
5. Open an issue on GitHub

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Add new scrapers for additional sources
- Improve documentation
- Submit pull requests

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

Built with:
- Python 3
- BeautifulSoup for web scraping
- Feedparser for RSS feeds
- Various amazing AI companies whose blogs we aggregate

---

**Happy reading! 🤖📰**
