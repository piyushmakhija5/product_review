# Search Provider Comparison

The system supports two search providers for product research. Choose based on your needs.

## Quick Comparison

| Feature | SerpAPI | Perplexity |
|---------|---------|------------|
| **Cost** | Free tier: 100/month | $5/month (5M tokens) |
| **Speed** | Fast (~1-2 sec) | Slower (~5-10 sec) |
| **Data Structure** | Structured JSON | LLM-extracted JSON |
| **Product Coverage** | Google Shopping results | Web search + analysis |
| **Price Accuracy** | High | High |
| **Feature Details** | Limited | Detailed |
| **Best For** | Price comparison | Detailed research |

## SerpAPI

### Pros:
- **Free tier available** (100 searches/month)
- **Fast and reliable** (~1-2 seconds per query)
- **Structured data** from Google Shopping
- **Great for price comparison** across retailers
- **High accuracy** on prices and availability

### Cons:
- Limited product descriptions
- May miss niche products
- Dependent on Google Shopping coverage

### Best Use Cases:
- Budget-conscious development
- Quick price comparisons
- Common electronics categories
- When speed matters

### Setup:
```bash
# In .env
SEARCH_PROVIDER=serpapi
SERPAPI_API_KEY=your-key-here
```

Get API key: https://serpapi.com/manage-api-key

## Perplexity

### Pros:
- **Web search + AI analysis** in one call
- **Better product descriptions** and features
- **Finds obscure products** that might not be on Google Shopping
- **Contextual information** about products
- **Smart extraction** of specs and features

### Cons:
- Costs $5/month for API access
- Slower (~5-10 seconds per query)
- May occasionally hallucinate details
- Requires validation of extracted data

### Best Use Cases:
- Detailed product research
- Niche or specialty products
- When you need rich product descriptions
- Professional/production use

### Setup:
```bash
# In .env
SEARCH_PROVIDER=perplexity
PERPLEXITY_API_KEY=pplx-your-key-here
```

Get API key: https://www.perplexity.ai/settings/api

## Switching Between Providers

Simply change the `SEARCH_PROVIDER` variable in your `.env` file:

```bash
# Use SerpAPI
SEARCH_PROVIDER=serpapi

# Or use Perplexity
SEARCH_PROVIDER=perplexity
```

Restart the application for changes to take effect.

## Recommendations

### For Development/Testing:
**Use SerpAPI** - The free tier is sufficient and it's faster for iteration.

### For Production:
**Consider your needs:**
- **Price comparison focus?** → SerpAPI
- **Detailed product info?** → Perplexity
- **Budget constrained?** → SerpAPI
- **Professional app?** → Perplexity

### Hybrid Approach:
You could also use both:
1. SerpAPI for initial fast search and price comparison
2. Perplexity for detailed analysis of top candidates

(This would require code modification to support both simultaneously)

## API Costs

### SerpAPI:
- Free: 100 searches/month
- $50/month: 5,000 searches
- $200/month: 30,000 searches

### Perplexity:
- $5/month: 5M tokens (~1,000-2,000 product searches)
- $20/month: 20M tokens (~4,000-8,000 product searches)

**Note:** Perplexity pricing is token-based, so actual costs depend on response length.
