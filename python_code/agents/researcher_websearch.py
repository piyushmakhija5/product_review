"""
Research Agent using Web Search - Much simpler and more reliable than scraping.
"""
from models.product import Product, PriceInfo, ReviewSummary
from models.requirements import UserRequirements
from utils.terminal import print_status, print_success, print_warning
from utils.llm import LLMClient
from config import Config
from typing import List
from datetime import datetime
import json


class WebSearchResearcher:
    """
    Agent that uses web search to find products instead of scraping.
    Much more reliable and doesn't get blocked.
    """

    def __init__(self):
        self.llm = LLMClient()

    def search(self, requirements: UserRequirements) -> List[Product]:
        """
        Search for products using web search.

        Args:
            requirements: User requirements

        Returns:
            List of Product objects
        """
        all_products = []

        # Search each retailer
        retailers = ['amazon', 'walmart', 'bestbuy']

        for retailer in retailers:
            print_status(f"Searching {retailer.title()} via web search...")

            try:
                products = self._search_retailer(retailer, requirements)
                if products:
                    print_success(f"  Found {len(products)} products on {retailer.title()}")
                    all_products.extend(products)
                else:
                    print_warning(f"  No products found on {retailer.title()}")

            except Exception as e:
                print_warning(f"  Error searching {retailer}: {str(e)}")
                if Config.DEBUG:
                    import traceback
                    traceback.print_exc()
                continue

        print_success(f"Total products found: {len(all_products)}")
        return all_products

    def _search_retailer(self, retailer: str, requirements: UserRequirements) -> List[Product]:
        """Search a specific retailer using web search and LLM extraction."""

        # Build search query
        query = self._build_search_query(retailer, requirements)

        if Config.DEBUG:
            print(f"[WebSearch] Query: {query}")

        try:
            # Use LLM with web search capability to find and extract products
            search_prompt = f"""
Search the web for products matching these requirements and extract product information.

REQUIREMENTS:
{requirements.model_dump_readable()}

RETAILER: {retailer}.com

Search for products on {retailer}.com that match these requirements. Find real products with:
- Product names
- Current prices (within the ${requirements.budget.max if requirements.budget else 'any'} budget)
- Ratings and review counts
- Key features that match the requirements
- Product URLs

Extract information for 3-5 products and return as JSON array:
[
  {{
    "name": "Actual Product Name",
    "price": 299.99,
    "rating": 4.5,
    "review_count": 1234,
    "features": ["feature1", "feature2"],
    "url": "actual product URL"
  }}
]

Focus on products that best match the user's needs for: {requirements.use_case}
"""

            # Use LLM to search and extract
            result = self.llm.structured_output(
                prompt=search_prompt,
                system="You are a product research assistant. Search the web and extract accurate product information.",
                temperature=0.7
            )

            # Convert to Product objects
            products = []
            if isinstance(result, list):
                product_list = result
            elif isinstance(result, dict) and 'products' in result:
                product_list = result['products']
            else:
                product_list = []

            for item in product_list:
                product = self._convert_to_product(item, retailer, requirements)
                if product:
                    products.append(product)

            return products

        except Exception as e:
            if Config.DEBUG:
                print(f"[WebSearch] Error: {e}")
                import traceback
                traceback.print_exc()
            return []

    def _build_search_query(self, retailer: str, requirements: UserRequirements) -> str:
        """Build search query for a specific retailer."""
        parts = [
            requirements.product_category,
            f"site:{retailer}.com"
        ]

        # Add budget constraint
        if requirements.budget:
            parts.append(f"under ${requirements.budget.max}")

        # Add key features
        if requirements.must_have_specs:
            for key, value in list(requirements.must_have_specs.items())[:2]:
                if isinstance(value, str):
                    parts.append(value)

        return " ".join(parts)

    def _convert_to_product(self, item: dict, retailer: str, requirements: UserRequirements) -> Product:
        """Convert search result item to Product object."""

        product_id = f"{retailer}_{item.get('name', 'unknown').replace(' ', '_')[:20]}"

        # Extract manufacturer from name (usually first word)
        name = item.get('name', '')
        manufacturer = name.split()[0] if name else "Unknown"

        # Create product
        product = Product(
            id=product_id,
            name=name,
            manufacturer=manufacturer,
            category=requirements.product_category,
            specifications={
                "features": item.get('features', [])
            },
            pricing={
                retailer: PriceInfo(
                    current_price=float(item.get('price', 0)),
                    in_stock=True,
                    url=item.get('url', ''),
                    last_updated=datetime.now()
                )
            },
            reviews={
                retailer: ReviewSummary(
                    average_rating=float(item.get('rating', 0)),
                    total_reviews=int(item.get('review_count', 0)),
                    rating_distribution={}
                )
            },
            scraped_at=datetime.now()
        )

        return product
