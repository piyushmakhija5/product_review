# Electronics Product Research Agent

An intelligent, terminal-based AI agent that helps you research and compare electronics products across multiple retailers. Get personalized recommendations based on your specific needs and constraints.

## Features

- **Intelligent Requirement Gathering**: Conversational AI that understands your needs
- **Multi-Retailer Research**: Searches Amazon, Walmart, and Best Buy
- **Deep Analysis**: AI-powered product comparison and ranking
- **Unknown Unknowns Detection**: Surfaces important considerations you might miss
- **Comprehensive Reports**: Detailed markdown reports with top 5 recommendations
- **Caching**: Smart caching to respect websites and speed up repeated searches

## Architecture

The system uses a multi-agent architecture:

1. **Planner Agent**: Analyzes requirements and determines what information is needed
2. **Collector Agent**: Conversationally gathers missing information
3. **Research Agent**: Coordinates web scraping across retailers
4. **Analyzer Agent**: Uses AI to analyze products and generate recommendations

## Prerequisites

- Python 3.10 or higher
- **LLM API key** for either:
  - Anthropic Claude (recommended)
  - Google Gemini
- **Search API key** - Choose one:
  - **SerpAPI** (recommended for structured data)
    - Free tier: 100 searches/month
    - Get at: https://serpapi.com/
  - **Perplexity** (better for detailed analysis)
    - $5/month for 5M tokens
    - Get at: https://www.perplexity.ai/settings/api

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd product_review
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys

# 1. Choose LLM Provider (Claude recommended):
ANTHROPIC_API_KEY=sk-ant-your-key-here
LLM_PROVIDER=claude

# OR for Gemini:
# GOOGLE_API_KEY=your-key-here
# LLM_PROVIDER=gemini

# 2. Choose Search Provider:
SEARCH_PROVIDER=serpapi

# If using SerpAPI (100 free searches/month):
SERPAPI_API_KEY=your-serpapi-key-here
# Get at: https://serpapi.com/manage-api-key

# If using Perplexity (better for detailed analysis):
# SEARCH_PROVIDER=perplexity
# PERPLEXITY_API_KEY=your-perplexity-key-here
# Get at: https://www.perplexity.ai/settings/api
```

### Choosing a Search Provider

**SerpAPI (Recommended for most users):**
- ✅ Free tier: 100 searches/month
- ✅ Returns structured Google Shopping data
- ✅ Best for price comparisons
- ✅ Fast and reliable
- ❌ Limited to search results metadata

**Perplexity (Better for detailed research):**
- ✅ Web search + LLM analysis in one call
- ✅ Better product descriptions and features
- ✅ More context about products
- ✅ Can find obscure products
- ❌ Costs $5/month (5M tokens)
- ❌ Slower than SerpAPI

**To switch providers:** Just change `SEARCH_PROVIDER` in your `.env` file!

### 5. (Optional) Install Playwright

If you need JavaScript rendering for scraping:

```bash
playwright install
```

## Usage

### Basic Usage

```bash
python main.py
```

Then follow the prompts. Example inputs:

```
"I need a gaming laptop under $1500 with good graphics"
"Looking for wireless earbuds with noise cancellation, budget $200"
"4K TV under $800 for gaming and streaming"
```

### Command Line Options

```bash
# Show help
python main.py --help

# Show version
python main.py --version
```

## Configuration

Edit `.env` to customize behavior:

```bash
# LLM Configuration
LLM_PROVIDER=claude                      # 'claude' or 'gemini'
LLM_MODEL=claude-sonnet-4.5-20250929    # Model to use

# Scraping Configuration
REQUEST_DELAY=2.5                        # Delay between requests (seconds)
MAX_RETRIES=3                            # Max retries for failed requests
MAX_PRODUCTS_PER_RETAILER=10             # Products to fetch per retailer

# Cache Configuration
CACHE_ENABLED=true                       # Enable/disable caching
CACHE_TTL_HOURS=4                        # Cache time-to-live

# Application Settings
DEBUG=false                              # Enable debug mode
SAVE_REPORTS=true                        # Auto-save reports to files
```

## Project Structure

```
product_review/
├── agents/              # AI agents
│   ├── planner.py      # Requirement analysis
│   ├── collector.py    # Information gathering
│   ├── researcher.py   # Product research coordinator
│   └── analyzer.py     # Analysis and reporting
├── scrapers/            # Web scrapers
│   ├── base.py         # Base scraper class
│   ├── amazon.py       # Amazon scraper
│   ├── walmart.py      # Walmart scraper (TODO)
│   └── bestbuy.py      # Best Buy scraper (TODO)
├── models/              # Data models
│   ├── requirements.py # User requirements
│   └── product.py      # Product data
├── utils/               # Utilities
│   ├── llm.py          # LLM client wrapper
│   ├── terminal.py     # Terminal UI
│   └── cache.py        # Caching system
├── prompts/             # LLM prompts
├── cache/               # Cached results
├── reports/             # Generated reports
├── docs/                # Documentation
│   └── planning.md     # Architecture planning
├── config.py            # Configuration
├── orchestrator.py      # Main workflow
├── main.py              # Entry point
└── requirements.txt     # Python dependencies
```

## How It Works

### Phase 1: Requirements Gathering

The system analyzes your initial input and asks follow-up questions to gather:
- Product category
- Budget (with flexibility)
- Must-have specifications
- Nice-to-have features
- Use case and context
- Deal-breakers

### Phase 2: Product Research

The Research Agent:
1. Builds search queries based on requirements
2. Scrapes product listings from each retailer
3. Filters by budget and availability
4. Deduplicates products across retailers
5. Caches results for efficiency

### Phase 3: Analysis

The Analyzer Agent uses AI to:
1. Score each product against requirements (0-100)
2. Consider price-to-value ratio
3. Analyze reviews and ratings
4. Identify pros, cons, and trade-offs
5. Surface "unknown unknowns"
6. Rank products and select top 5

### Phase 4: Report Generation

Generates a comprehensive markdown report including:
- Top 5 product recommendations
- Match scores and reasoning
- Detailed comparisons
- Price comparisons across retailers
- Unknown unknowns and considerations
- Final recommendation with clear reasoning
- Actionable next steps

## Example Output

```markdown
# Electronics Purchase Recommendation Report

## Your Requirements
- Product: Gaming Laptop
- Budget: $1000 - $1500
- Use Case: Gaming and content creation
- Must-Have: RTX 4060, 16GB RAM, SSD

## Top 5 Recommendations

### 1. ASUS ROG Strix G16 - 94/100

**Best Price:** $1,299.99 at Amazon

**Why This Product:**
- Exceeds requirements with RTX 4060
- 16GB DDR5 RAM, expandable
- 1TB NVMe SSD
- Excellent cooling system
- High refresh rate display

**Unknown Unknowns:**
- Battery life is only 4-5 hours under load
- Weighs 5.5 lbs - not ideal for portability
- Some users report loud fans during gaming

...
```

## Current Capabilities

**Product Search (Two Options):**

1. **SerpAPI Mode:**
   - Uses Google Shopping for structured product data
   - Fast, reliable, with free tier (100 searches/month)
   - Returns prices, ratings, review counts, and direct links
   - Best for price comparison across retailers

2. **Perplexity Mode:**
   - Web search + AI analysis combined
   - Better product descriptions and feature extraction
   - More contextual information about products
   - Can find less common products
   - $5/month for API access

**Both modes:**
- Search across Amazon, Walmart, Best Buy, and other retailers
- Real-time product data
- No scraping blocks or CAPTCHA issues
- Easy switching via `.env` configuration

**Current Limitations:**
1. **Reviews**: Basic review data (ratings and counts, no detailed sentiment analysis yet)
2. **Specs**: Specification detail varies by search provider
3. **Categories**: Works best with common electronics categories

## Future Enhancements

See `docs/planning.md` for full roadmap. Priorities:

1. Implement Walmart and Best Buy scrapers
2. Enhanced review analysis with sentiment
3. Detailed specification extraction
4. Manufacturer site integration
5. Price history tracking
6. More product categories
7. Web UI

## Troubleshooting

### "Configuration errors: ANTHROPIC_API_KEY is required"

Make sure you've:
1. Created a `.env` file
2. Added your API key
3. Set the correct LLM_PROVIDER

### "No products found"

Try:
1. Increasing your budget
2. Relaxing some requirements
3. Using more general search terms
4. Checking if products are in stock

### Scraping errors

- Websites may block scrapers - this is expected
- Enable DEBUG=true to see detailed errors
- Try clearing cache: `rm -rf cache/*`
- Consider using official APIs for production

### Rate limiting

If you hit rate limits:
- Increase REQUEST_DELAY in .env
- Enable caching
- Reduce MAX_PRODUCTS_PER_RETAILER

## Development

### Running Tests

```bash
pytest tests/
```

### Debug Mode

```bash
# Enable in .env
DEBUG=true

# Or set environment variable
DEBUG=true python main.py
```

### Clear Cache

```bash
rm -rf cache/*
```

### Code Style

This project follows PEP 8. Format with:

```bash
black .
```

## Legal & Ethical Considerations

**Important**: This tool scrapes public websites for research purposes.

- Respects robots.txt
- Implements polite delays between requests
- Caches results to minimize load
- For educational/personal use

For production use:
- Consider official retailer APIs
- Review each site's Terms of Service
- Implement more sophisticated rate limiting
- Add proper error handling and monitoring

## License

[Your License Here]

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues, questions, or feedback:
- Open an issue on GitHub
- Check `docs/planning.md` for architecture details
- Enable DEBUG mode for detailed error messages

## Acknowledgments

- Built with Claude Sonnet 4.5 / Gemini 3
- Uses Rich library for beautiful terminal UI
- Inspired by the need for better product research tools

---

**Note**: This is an MVP implementation focused on core functionality. See `docs/planning.md` for the complete architecture and future enhancements.
