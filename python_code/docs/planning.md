# Electronics Product Research Agent - Architecture & Planning

## Executive Summary

A simple, terminal-based AI agent system that helps users research electronics products across Amazon, Walmart, and Best Buy. Built with Python, powered by Claude Sonnet 4.5 or Gemini 3, focusing on simplicity and direct LLM capabilities (thinking, tool use).

---

## 1. System Overview

### 1.1 Core Objectives
- Collect comprehensive user requirements through terminal chat
- Research products across multiple retailers
- Analyze and rank top 5 products
- Surface "unknown unknowns"
- Generate actionable text reports

### 1.2 Simplified Architecture

```
Terminal Interface (CLI)
         ↓
   Main Orchestrator
         ↓
    ┌────┴────┬────────┬─────────┐
    ↓         ↓        ↓         ↓
Planner   Info     Research  Analysis
         Collector            & Report
```

**Key Principle:** Simple Python orchestration, direct LLM API calls, no heavy frameworks.

---

## 2. Agent Design (Simplified)

### 2.1 Planner Agent

**Purpose:** Decide if we have enough info or need to ask more questions

**Implementation:**
- Single LLM call with structured output
- Uses Claude/Gemini's tool use capability
- Returns: `{status: "ready" | "need_more_info", missing_fields: [...]}`

**Prompt Structure:**
```python
system_prompt = """
You are a requirement analyzer for electronics purchases.
Analyze if we have enough information to proceed with product research.

Required information:
- Product category (specific, not vague)
- Budget (at least a range)
- Key specifications needed
- Primary use case

Return JSON:
{
  "status": "ready" or "need_more_info",
  "missing_fields": ["field1", "field2"],
  "confidence": 0.0-1.0
}
"""
```

### 2.2 Information Collector Agent

**Purpose:** Chat with user to fill information gaps

**Implementation:**
- Conversational loop in terminal
- Uses Claude/Gemini's extended thinking for natural dialogue
- Maintains context in simple Python dict
- Asks one question at a time

**Flow:**
```python
while not requirements_complete:
    question = generate_next_question(missing_info)
    print(f"Agent: {question}")
    user_response = input("You: ")
    update_requirements(user_response)
    requirements_complete = check_completeness()
```

### 2.3 Research Agent

**Purpose:** Scrape product data from web

**Implementation:**
- Python functions with BeautifulSoup4 + requests
- Playwright for JS-heavy pages (if needed)
- Direct web scraping - no APIs initially
- Simple retry logic

**Research Steps:**
```python
def research_products(requirements):
    products = []

    # Scrape each retailer
    for retailer in ['amazon', 'walmart', 'bestbuy']:
        search_results = scrape_retailer(retailer, requirements)
        products.extend(search_results)

    # Deduplicate by model number
    unique_products = deduplicate(products)

    # Get additional details for top candidates
    for product in unique_products[:15]:
        product.reviews = scrape_reviews(product)
        product.specs = scrape_full_specs(product)

    return unique_products
```

**Scraping Strategy:**
- Start with simple requests + BeautifulSoup
- Add Playwright only if JavaScript rendering needed
- Respectful delays (2-3 seconds between requests)
- Cache results in local JSON files

### 2.4 Analysis & Report Agent

**Purpose:** Analyze products and generate report

**Implementation:**
- Single LLM call with all product data
- Uses Claude/Gemini's extended thinking for deep analysis
- Structured output for rankings
- Text-based report generation

**Process:**
```python
def analyze_and_report(products, requirements):
    # Let LLM analyze with extended thinking
    analysis_prompt = f"""
    Analyze these {len(products)} products against requirements.
    Requirements: {requirements}
    Products: {products}

    Tasks:
    1. Score each product (0-100)
    2. Identify top 5
    3. Find pros/cons from reviews
    4. Surface unknown unknowns
    5. Generate comparison

    Think deeply about trade-offs and hidden considerations.
    """

    report = llm_call(analysis_prompt, extended_thinking=True)
    return report
```

---

## 3. Technical Stack (Simple & Practical)

### 3.1 Core Technologies

**Language:** Python 3.10+

**LLM Integration:**
- **Primary:** Claude Sonnet 4.5 (Anthropic API)
- **Alternative:** Gemini 3 (Google API)
- **Why:** Both have native thinking + tool use, no framework needed
- **Library:** `anthropic` or `google-generativeai` SDK

**Web Scraping:**
- `requests` - HTTP calls
- `beautifulsoup4` - HTML parsing
- `playwright` - JavaScript rendering (if needed)
- `lxml` - Fast parsing

**Data Handling:**
- `pydantic` - Data validation and models
- `json` - Simple storage
- File system - No database initially

**Terminal UI:**
- `rich` - Pretty terminal output
- `prompt_toolkit` - Better input handling
- Built-in `input()` - Fallback

**Configuration:**
- `python-dotenv` - Load .env files
- `pyyaml` - Config files (optional)

**No Heavy Frameworks:**
- ❌ LangChain (as requested)
- ✅ LangGraph (optional, for visual workflow only)
- ✅ Direct API calls

### 3.2 Project Structure

```
product_review/
├── .env                          # API keys (gitignored)
├── .env.example                  # Template
├── requirements.txt              # Dependencies
├── config.py                     # Load environment vars
├── main.py                       # Entry point
├── orchestrator.py               # Main workflow logic
├── agents/
│   ├── __init__.py
│   ├── planner.py               # Requirement analysis
│   ├── collector.py             # Info gathering
│   ├── researcher.py            # Web scraping
│   └── analyzer.py              # Analysis & reporting
├── scrapers/
│   ├── __init__.py
│   ├── base.py                  # Base scraper class
│   ├── amazon.py
│   ├── walmart.py
│   └── bestbuy.py
├── models/
│   ├── __init__.py
│   ├── requirements.py          # Pydantic models
│   └── product.py
├── utils/
│   ├── __init__.py
│   ├── llm.py                   # LLM wrapper
│   ├── terminal.py              # Terminal UI helpers
│   └── cache.py                 # Simple caching
├── prompts/
│   ├── planner_prompt.txt
│   ├── collector_prompt.txt
│   ├── analyzer_prompt.txt
│   └── report_template.txt
├── cache/                        # Cached scraping results
├── docs/
│   └── planning.md
└── tests/                        # Unit tests
```

### 3.3 Environment Configuration

**.env file:**
```bash
# LLM API Keys (use one)
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...

# LLM Selection
LLM_PROVIDER=claude  # or 'gemini'
LLM_MODEL=claude-sonnet-4.5-20250929

# Scraping
USER_AGENT=Mozilla/5.0 ...
REQUEST_DELAY=2.5
MAX_RETRIES=3

# Application
DEBUG=false
CACHE_ENABLED=true
CACHE_TTL_HOURS=4
```

**config.py:**
```python
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # LLM
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'claude')
    LLM_MODEL = os.getenv('LLM_MODEL', 'claude-sonnet-4.5-20250929')

    # Scraping
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0...')
    REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', 2.5))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))

    # App
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_TTL_HOURS = int(os.getenv('CACHE_TTL_HOURS', 4))
```

---

## 4. Data Models

### 4.1 Pydantic Models

**models/requirements.py:**
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class BudgetConstraint(BaseModel):
    min: Optional[float] = None
    max: float
    flexible: bool = False
    flexibility_percent: Optional[float] = None

class UserRequirements(BaseModel):
    product_category: str
    budget: BudgetConstraint
    must_have_specs: Dict[str, any] = {}
    nice_to_have_specs: Dict[str, any] = {}
    deal_breakers: List[str] = []
    use_case: str = ""
    priorities: List[str] = []

    completeness_score: float = 0.0

    def is_complete(self) -> bool:
        return (
            self.product_category and
            self.budget.max > 0 and
            len(self.must_have_specs) > 0 and
            self.use_case and
            self.completeness_score >= 0.8
        )
```

**models/product.py:**
```python
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class PriceInfo(BaseModel):
    current_price: float
    original_price: Optional[float] = None
    discount_percent: Optional[float] = None
    in_stock: bool
    url: str
    last_updated: datetime

class ReviewSummary(BaseModel):
    average_rating: float
    total_reviews: int
    rating_distribution: Dict[int, int]  # {5: 120, 4: 30, ...}
    common_pros: List[str] = []
    common_cons: List[str] = []
    recent_reviews_sample: List[str] = []

class Product(BaseModel):
    id: str
    name: str
    manufacturer: str
    model_number: Optional[str] = None
    category: str

    # Specs
    specifications: Dict[str, any]

    # Pricing from different retailers
    pricing: Dict[str, PriceInfo]  # {'amazon': PriceInfo, ...}

    # Reviews
    reviews: Dict[str, ReviewSummary]  # {'amazon': ReviewSummary, ...}

    # URLs
    manufacturer_url: Optional[str] = None

    # Metadata
    scraped_at: datetime

    def get_best_price(self) -> tuple[str, float]:
        """Returns (retailer, price) for best deal"""
        best = min(
            self.pricing.items(),
            key=lambda x: x[1].current_price if x[1].in_stock else float('inf')
        )
        return best[0], best[1].current_price

    def get_average_rating(self) -> float:
        """Average rating across all retailers"""
        ratings = [r.average_rating for r in self.reviews.values()]
        return sum(ratings) / len(ratings) if ratings else 0.0

class AnalysisResult(BaseModel):
    product: Product
    match_score: float  # 0-100
    requirement_fulfillment: Dict[str, bool]
    value_score: float
    pros: List[str]
    cons: List[str]
    unknown_unknowns: List[str]
    rank: int
```

---

## 5. Workflow Implementation

### 5.1 Main Orchestrator

**orchestrator.py:**
```python
from agents.planner import PlannerAgent
from agents.collector import CollectorAgent
from agents.researcher import ResearchAgent
from agents.analyzer import AnalyzerAgent
from models.requirements import UserRequirements
from utils.terminal import print_header, print_status

class WorkflowOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.collector = CollectorAgent()
        self.researcher = ResearchAgent()
        self.analyzer = AnalyzerAgent()

    def run(self, initial_input: str):
        """Main workflow execution"""

        # Step 1: Initial Planning
        print_header("Analyzing your requirements...")
        plan = self.planner.analyze(initial_input)
        requirements = plan.requirements

        # Step 2: Collect More Info if Needed
        while plan.status == "need_more_info":
            print_status("Need more information...")
            requirements = self.collector.gather(
                requirements,
                plan.missing_fields
            )
            plan = self.planner.analyze_requirements(requirements)

        print_status("✓ Requirements complete!")

        # Step 3: Research
        print_header("Researching products...")
        print_status("This may take 2-3 minutes...")
        products = self.researcher.search(requirements)
        print_status(f"✓ Found {len(products)} products")

        # Step 4: Analysis & Report
        print_header("Analyzing and generating report...")
        report = self.analyzer.analyze_and_report(products, requirements)

        # Step 5: Display Report
        print_header("Your Personalized Report")
        print(report)

        # Save report
        self.save_report(report, requirements)

        return report
```

### 5.2 LLM Wrapper

**utils/llm.py:**
```python
from anthropic import Anthropic
import google.generativeai as genai
from config import Config
import json

class LLMClient:
    def __init__(self):
        self.provider = Config.LLM_PROVIDER

        if self.provider == 'claude':
            self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.model = Config.LLM_MODEL
        elif self.provider == 'gemini':
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.client = genai.GenerativeModel(Config.LLM_MODEL)

    def call(
        self,
        prompt: str,
        system: str = "",
        thinking: bool = False,
        tools: list = None,
        response_format: dict = None
    ):
        """Unified LLM call for both Claude and Gemini"""

        if self.provider == 'claude':
            return self._call_claude(prompt, system, thinking, tools)
        else:
            return self._call_gemini(prompt, system, thinking)

    def _call_claude(self, prompt, system, thinking, tools):
        """Claude Sonnet 4.5 with thinking support"""
        messages = [{"role": "user", "content": prompt}]

        params = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages,
        }

        if system:
            params["system"] = system

        if thinking:
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": 2000
            }

        if tools:
            params["tools"] = tools

        response = self.client.messages.create(**params)
        return response

    def _call_gemini(self, prompt, system, thinking):
        """Gemini 3 call"""
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = self.client.generate_content(full_prompt)
        return response

    def structured_output(self, prompt: str, system: str, output_schema: dict):
        """Get structured JSON output"""
        full_prompt = f"{prompt}\n\nReturn valid JSON matching this schema:\n{json.dumps(output_schema, indent=2)}"
        response = self.call(full_prompt, system)

        # Extract JSON from response
        content = self._extract_content(response)
        return json.loads(content)

    def _extract_content(self, response) -> str:
        """Extract text content from LLM response"""
        if self.provider == 'claude':
            return response.content[0].text
        else:
            return response.text
```

---

## 6. Agent Implementation Details

### 6.1 Planner Agent

**agents/planner.py:**
```python
from utils.llm import LLMClient
from models.requirements import UserRequirements
import json

class PlannerAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = self._load_prompt()

    def analyze(self, user_input: str):
        """Analyze if we have enough information"""

        prompt = f"""
        User input: {user_input}

        Determine if we have enough information to research products.
        Return JSON with this structure:
        {{
            "status": "ready" or "need_more_info",
            "missing_fields": ["field1", "field2"],
            "extracted_requirements": {{
                "product_category": "...",
                "budget": {{"max": 0, "flexible": false}},
                "must_have_specs": {{}},
                "use_case": "..."
            }},
            "confidence": 0.0-1.0
        }}
        """

        result = self.llm.call(
            prompt=prompt,
            system=self.system_prompt,
            thinking=True  # Use extended thinking
        )

        # Parse response
        return self._parse_plan(result)
```

### 6.2 Researcher Agent

**agents/researcher.py:**
```python
from scrapers.amazon import AmazonScraper
from scrapers.walmart import WalmartScraper
from scrapers.bestbuy import BestBuyScraper
from models.product import Product
from utils.cache import Cache
import time

class ResearchAgent:
    def __init__(self):
        self.scrapers = {
            'amazon': AmazonScraper(),
            'walmart': WalmartScraper(),
            'bestbuy': BestBuyScraper()
        }
        self.cache = Cache()

    def search(self, requirements) -> list[Product]:
        """Search across all retailers"""
        all_products = []

        for retailer_name, scraper in self.scrapers.items():
            print(f"  Searching {retailer_name}...")

            try:
                # Check cache
                cache_key = self._make_cache_key(retailer_name, requirements)
                cached = self.cache.get(cache_key)

                if cached:
                    products = cached
                else:
                    products = scraper.search(requirements)
                    self.cache.set(cache_key, products)

                all_products.extend(products)
                time.sleep(Config.REQUEST_DELAY)

            except Exception as e:
                print(f"  ⚠ Error with {retailer_name}: {e}")
                continue

        # Deduplicate
        unique = self._deduplicate(all_products)
        return unique
```

### 6.3 Analyzer Agent

**agents/analyzer.py:**
```python
from utils.llm import LLMClient
from models.product import Product, AnalysisResult
from typing import List

class AnalyzerAgent:
    def __init__(self):
        self.llm = LLMClient()

    def analyze_and_report(
        self,
        products: List[Product],
        requirements
    ) -> str:
        """Analyze products and generate report"""

        # Prepare data for LLM
        product_data = self._prepare_product_data(products)

        prompt = f"""
        You are an expert electronics advisor. Analyze these products and create a comprehensive report.

        USER REQUIREMENTS:
        {requirements.model_dump_json(indent=2)}

        PRODUCTS FOUND:
        {product_data}

        YOUR TASK:
        1. Score each product (0-100) based on requirement match
        2. Identify top 5 products
        3. For each top product:
           - Explain why it's a good match
           - List pros and cons from reviews
           - Identify "unknown unknowns" (important factors user didn't consider)
           - Compare prices across retailers
        4. Create a comparison matrix
        5. Give your final recommendation

        Use your extended thinking to deeply analyze trade-offs.

        Format as a clear, text-only markdown report.
        """

        response = self.llm.call(
            prompt=prompt,
            system="You are a helpful electronics research assistant.",
            thinking=True  # Enable deep analysis
        )

        report = self._extract_report(response)
        return report
```

---

## 7. Scraping Implementation

### 7.1 Base Scraper

**scrapers/base.py:**
```python
import requests
from bs4 import BeautifulSoup
from config import Config
import time

class BaseScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': Config.USER_AGENT})

    def get(self, url: str, retries: int = 3):
        """GET request with retry logic"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt)

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML"""
        return BeautifulSoup(html, 'lxml')
```

### 7.2 Amazon Scraper (Example)

**scrapers/amazon.py:**
```python
from .base import BaseScraper
from models.product import Product, PriceInfo, ReviewSummary
from datetime import datetime
import re

class AmazonScraper(BaseScraper):
    BASE_URL = "https://www.amazon.com"

    def search(self, requirements) -> list[Product]:
        """Search Amazon for products"""
        query = self._build_search_query(requirements)
        url = f"{self.BASE_URL}/s?k={query}"

        response = self.get(url)
        soup = self.parse_html(response.text)

        products = []
        items = soup.select('[data-component-type="s-search-result"]')

        for item in items[:10]:  # Top 10 results
            try:
                product = self._extract_product(item)
                if product:
                    products.append(product)
            except Exception as e:
                continue

        return products

    def _extract_product(self, item) -> Product:
        """Extract product details from search result"""
        # Title
        title_elem = item.select_one('h2 a span')
        name = title_elem.text.strip() if title_elem else ""

        # Price
        price_elem = item.select_one('.a-price .a-offscreen')
        price = self._parse_price(price_elem.text) if price_elem else 0

        # Rating
        rating_elem = item.select_one('.a-icon-star-small')
        rating = self._parse_rating(rating_elem.text) if rating_elem else 0

        # URL
        link_elem = item.select_one('h2 a')
        url = self.BASE_URL + link_elem['href'] if link_elem else ""

        # ... extract more details

        return Product(
            id=self._generate_id(name),
            name=name,
            manufacturer=self._extract_brand(name),
            category=requirements.product_category,
            specifications={},  # Will be enriched later
            pricing={
                'amazon': PriceInfo(
                    current_price=price,
                    in_stock=True,
                    url=url,
                    last_updated=datetime.now()
                )
            },
            reviews={
                'amazon': ReviewSummary(
                    average_rating=rating,
                    total_reviews=0,
                    rating_distribution={}
                )
            },
            scraped_at=datetime.now()
        )
```

---

## 8. Terminal UI

### 8.1 Rich Terminal Output

**utils/terminal.py:**
```python
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.table import Table

console = Console()

def print_header(text: str):
    console.print(Panel(text, style="bold blue"))

def print_status(text: str):
    console.print(f"[yellow]►[/yellow] {text}")

def print_success(text: str):
    console.print(f"[green]✓[/green] {text}")

def print_error(text: str):
    console.print(f"[red]✗[/red] {text}")

def print_report(markdown_text: str):
    md = Markdown(markdown_text)
    console.print(md)

def print_product_table(products):
    table = Table(title="Top Products")
    table.add_column("Rank", style="cyan")
    table.add_column("Product", style="green")
    table.add_column("Price", style="yellow")
    table.add_column("Rating", style="magenta")

    for i, p in enumerate(products[:5], 1):
        retailer, price = p.get_best_price()
        table.add_row(
            str(i),
            p.name[:50] + "..." if len(p.name) > 50 else p.name,
            f"${price:.2f}",
            f"{p.get_average_rating():.1f}/5"
        )

    console.print(table)
```

### 8.2 Main Entry Point

**main.py:**
```python
from orchestrator import WorkflowOrchestrator
from utils.terminal import console, print_header, print_error
from rich.prompt import Prompt
import sys

def main():
    console.clear()
    print_header("🔍 Electronics Research Agent")

    console.print("\nWelcome! I'll help you find the perfect electronics product.\n")
    console.print("Tell me what you're looking for (e.g., 'I need a laptop for video editing under $1500')\n")

    try:
        # Get initial input
        user_input = Prompt.ask("[bold cyan]You[/bold cyan]")

        if not user_input.strip():
            print_error("Please provide some details about what you're looking for.")
            sys.exit(1)

        # Run workflow
        orchestrator = WorkflowOrchestrator()
        report = orchestrator.run(user_input)

        console.print("\n[green]Report generated successfully![/green]")
        console.print("Check the 'reports' directory for saved report.\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user. Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        print_error(f"An error occurred: {e}")
        if Config.DEBUG:
            raise
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 9. Implementation Phases (Simplified)

### Phase 1: Core MVP (Week 1)
**Goal:** End-to-end flow with minimal features

- [ ] Setup project structure
- [ ] Implement config.py with .env loading
- [ ] Create basic LLM wrapper (Claude or Gemini)
- [ ] Implement Planner agent (simple version)
- [ ] Implement Info Collector (basic questions)
- [ ] Basic Amazon scraper only
- [ ] Simple analysis (rule-based scoring)
- [ ] Text report generation
- [ ] Terminal UI with rich

**Deliverable:** Working prototype that can research laptops on Amazon

### Phase 2: Multi-Retailer (Week 2)
- [ ] Add Walmart scraper
- [ ] Add Best Buy scraper
- [ ] Implement deduplication logic
- [ ] Add caching system
- [ ] Improve error handling

**Deliverable:** Research across 3 retailers

### Phase 3: Enhanced Analysis (Week 3)
- [ ] LLM-powered analysis agent
- [ ] Unknown unknowns detection
- [ ] Better scoring algorithm
- [ ] Improved report format
- [ ] Add review scraping and analysis

**Deliverable:** High-quality recommendations with insights

### Phase 4: Polish & Optimization
- [ ] Performance optimization
- [ ] Better error messages
- [ ] Add more product categories
- [ ] Comprehensive testing
- [ ] Documentation

**Deliverable:** Production-ready CLI tool

---

## 10. Testing Strategy

### 10.1 Unit Tests
```python
# tests/test_planner.py
def test_planner_detects_missing_budget():
    planner = PlannerAgent()
    result = planner.analyze("I need a laptop for gaming")
    assert result.status == "need_more_info"
    assert "budget" in result.missing_fields

# tests/test_scrapers.py
def test_amazon_scraper_extracts_price():
    scraper = AmazonScraper()
    # Test with mock HTML
    ...
```

### 10.2 Integration Tests
```python
def test_end_to_end_flow():
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.run(
        "I need a gaming laptop under $1200 with RTX 4060"
    )
    assert result is not None
    assert len(result.top_products) == 5
```

---

## 11. Next Steps

### Immediate Actions:
1. **Setup Project**
   ```bash
   mkdir product_review
   cd product_review
   python -m venv venv
   source venv/bin/activate
   ```

2. **Create requirements.txt**
   ```
   anthropic>=0.40.0
   google-generativeai>=0.8.0
   python-dotenv>=1.0.0
   pydantic>=2.0.0
   requests>=2.31.0
   beautifulsoup4>=4.12.0
   lxml>=5.0.0
   rich>=13.0.0
   playwright>=1.40.0  # optional
   pytest>=7.4.0
   ```

3. **Create .env.example**
   ```bash
   ANTHROPIC_API_KEY=your_key_here
   GOOGLE_API_KEY=your_key_here
   LLM_PROVIDER=claude
   LLM_MODEL=claude-sonnet-4.5-20250929
   ```

4. **Start Implementation**
   - Begin with config.py
   - Then utils/llm.py
   - Then agents one by one

---

## 12. Key Design Principles

1. **Simplicity First:** Direct API calls, no heavy frameworks
2. **Progressive Enhancement:** Start simple, add complexity only when needed
3. **Fail Gracefully:** Continue with partial data if some scrapers fail
4. **Cache Aggressively:** Respect websites, reduce redundant requests
5. **Terminal-Focused:** Rich CLI experience before web UI
6. **LLM-Native:** Leverage Claude/Gemini's thinking and tool use directly

---

## 13. Success Criteria

**Must Have:**
- ✓ Collects complete user requirements
- ✓ Scrapes 3 retailers (Amazon, Walmart, Best Buy)
- ✓ Returns top 5 ranked products
- ✓ Includes pricing comparison
- ✓ Generates readable text report
- ✓ Terminal-based interface

**Nice to Have:**
- Unknown unknowns detection
- Review sentiment analysis
- Price history tracking
- Save/load sessions

---

## Conclusion

This simplified architecture focuses on practical implementation with modern LLMs' native capabilities. No heavy frameworks, just Python, direct API calls, and smart scraping. The terminal-first approach lets us focus on core functionality before building fancy UIs.

**Philosophy:** Build the simplest thing that works, then iterate based on real usage.
