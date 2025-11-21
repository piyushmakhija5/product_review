"""
Research Agent - Coordinates web scraping across multiple retailers.
"""
from scrapers.amazon import AmazonScraper
from scrapers.walmart import WalmartScraper
from scrapers.bestbuy import BestBuyScraper
from models.product import Product
from models.requirements import UserRequirements
from utils.cache import Cache, make_cache_key
from utils.terminal import print_status, print_success, print_warning
from config import Config
from typing import List, Dict
import time


class ResearchAgent:
    """
    Agent responsible for researching products across multiple retailers.
    """

    def __init__(self):
        self.scrapers = {
            'amazon': AmazonScraper(),
            'walmart': WalmartScraper(),
            'bestbuy': BestBuyScraper()
        }
        self.cache = Cache()

    def search(self, requirements: UserRequirements) -> List[Product]:
        """
        Search for products across all retailers.

        Args:
            requirements: User requirements

        Returns:
            List of unique products from all retailers
        """
        all_products = []

        for retailer_name, scraper in self.scrapers.items():
            print_status(f"Searching {retailer_name.title()}...")

            try:
                # Check cache first
                cache_key = self._make_cache_key(retailer_name, requirements)
                cached_products = self.cache.get(cache_key)

                if cached_products and Config.CACHE_ENABLED:
                    print_status(f"  Using cached results for {retailer_name}")
                    products = self._deserialize_products(cached_products)
                else:
                    # Scrape fresh data
                    products = scraper.search(requirements)

                    # Cache results
                    if products and Config.CACHE_ENABLED:
                        serialized = self._serialize_products(products)
                        self.cache.set(cache_key, serialized)

                if products:
                    print_success(f"  Found {len(products)} products on {retailer_name.title()}")
                    all_products.extend(products)
                else:
                    print_warning(f"  No products found on {retailer_name.title()}")

                # Respectful delay between retailers
                time.sleep(Config.REQUEST_DELAY)

            except Exception as e:
                print_warning(f"  Error searching {retailer_name}: {str(e)}")
                if Config.DEBUG:
                    raise
                continue

        # Deduplicate products
        unique_products = self._deduplicate_products(all_products)

        print_success(f"Total unique products found: {len(unique_products)}")

        return unique_products

    def _make_cache_key(self, retailer: str, requirements: UserRequirements) -> str:
        """Generate cache key for search results."""
        return make_cache_key(
            retailer,
            requirements.product_category,
            requirements.budget.max if requirements.budget else 0,
            str(requirements.must_have_specs)
        )

    def _deduplicate_products(self, products: List[Product]) -> List[Product]:
        """
        Deduplicate products by merging those with similar names or model numbers.

        Args:
            products: List of products

        Returns:
            Deduplicated list
        """
        if not products:
            return []

        # Group by normalized name
        product_map: Dict[str, Product] = {}

        for product in products:
            # Create a normalized key
            key = self._normalize_product_key(product)

            if key in product_map:
                # Merge pricing and review data
                existing = product_map[key]
                existing.pricing.update(product.pricing)
                existing.reviews.update(product.reviews)
            else:
                product_map[key] = product

        return list(product_map.values())

    def _normalize_product_key(self, product: Product) -> str:
        """
        Create a normalized key for product deduplication.

        Args:
            product: Product object

        Returns:
            Normalized key string
        """
        # Use model number if available
        if product.model_number:
            return f"{product.manufacturer.lower()}:{product.model_number.lower()}"

        # Otherwise use normalized name
        # Remove common words and normalize
        name = product.name.lower()
        for word in ['the', 'with', 'for', 'and', '-', ',']:
            name = name.replace(word, ' ')

        # Keep first 50 chars of normalized name
        name = ' '.join(name.split())[:50]

        return f"{product.manufacturer.lower()}:{name}"

    def _serialize_products(self, products: List[Product]) -> List[dict]:
        """Convert products to JSON-serializable format for caching."""
        return [p.model_dump() for p in products]

    def _deserialize_products(self, data: List[dict]) -> List[Product]:
        """Convert cached data back to Product objects."""
        return [Product(**item) for item in data]

    def enrich_products(self, products: List[Product]) -> List[Product]:
        """
        Enrich products with additional details.
        For MVP, this is a placeholder.

        Args:
            products: List of products to enrich

        Returns:
            Enriched products
        """
        # In a full implementation, this would:
        # 1. Visit product detail pages
        # 2. Scrape full specifications
        # 3. Get more reviews
        # 4. Check manufacturer sites

        return products
