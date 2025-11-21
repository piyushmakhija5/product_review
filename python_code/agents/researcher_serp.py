"""
Research Agent using SerpAPI for real web search.
Much more reliable than web scraping - uses Google Shopping and site-specific searches.
"""
from serpapi import GoogleSearch
from models.product import Product, PriceInfo, ReviewSummary
from models.requirements import UserRequirements
from utils.terminal import print_status, print_success, print_warning
from config import Config
from typing import List, Dict, Any
from datetime import datetime
import hashlib


class SerpAPIResearcher:
    """
    Agent that uses SerpAPI to search for products across retailers.
    Uses Google Shopping for product search.
    """

    def __init__(self):
        if not Config.SERPAPI_API_KEY:
            raise ValueError("SERPAPI_API_KEY is required. Get one at https://serpapi.com/")
        self.api_key = Config.SERPAPI_API_KEY

    def search(self, requirements: UserRequirements) -> List[Product]:
        """
        Search for products using SerpAPI.

        Args:
            requirements: User requirements

        Returns:
            List of Product objects
        """
        print_status("Searching via Google Shopping...")

        try:
            # Use Google Shopping search
            products = self._search_google_shopping(requirements)

            if products:
                print_success(f"Found {len(products)} products via Google Shopping")
            else:
                print_warning("No products found")

            return products

        except Exception as e:
            print_warning(f"Search error: {str(e)}")
            if Config.DEBUG:
                import traceback
                traceback.print_exc()
            return []

    def _search_google_shopping(self, requirements: UserRequirements) -> List[Product]:
        """Search Google Shopping for products."""

        # Build search query
        query = self._build_search_query(requirements)

        if Config.DEBUG:
            print(f"[SerpAPI] Query: {query}")

        # SerpAPI parameters
        params = {
            "engine": "google_shopping",
            "q": query,
            "api_key": self.api_key,
            "num": 20,  # Get more results
        }

        # Add price filter if budget specified
        if requirements.budget:
            params["tbs"] = f"mr:1,price:1,ppr_max:{int(requirements.budget.max)}"

        try:
            search = GoogleSearch(params)
            results = search.get_dict()

            if Config.DEBUG:
                print(f"[SerpAPI] Raw results keys: {results.keys()}")

            # Extract products from shopping results
            products = []
            shopping_results = results.get("shopping_results", [])

            if Config.DEBUG:
                print(f"[SerpAPI] Found {len(shopping_results)} shopping results")

            for item in shopping_results[:Config.MAX_PRODUCTS_PER_RETAILER]:
                product = self._extract_product_from_shopping_result(item, requirements)
                if product:
                    products.append(product)

            return products

        except Exception as e:
            if Config.DEBUG:
                print(f"[SerpAPI] Error: {e}")
                import traceback
                traceback.print_exc()
            raise

    def _build_search_query(self, requirements: UserRequirements) -> str:
        """Build search query from requirements."""
        parts = [requirements.product_category]

        # Add key features to search
        if requirements.must_have_specs:
            for key, value in list(requirements.must_have_specs.items())[:3]:
                if isinstance(value, str) and len(value.split()) <= 4:
                    parts.append(value)

        # Add use case hint if short
        if requirements.use_case and len(requirements.use_case.split()) <= 3:
            parts.append(requirements.use_case)

        query = " ".join(parts)

        # Limit query length
        if len(query) > 100:
            query = query[:100]

        return query

    def _extract_product_from_shopping_result(
        self,
        item: Dict[str, Any],
        requirements: UserRequirements
    ) -> Product:
        """Extract product from Google Shopping result."""

        try:
            # Extract basic info
            name = item.get("title", "Unknown Product")
            price_str = item.get("price", "0")

            # Parse price
            price = self._parse_price(price_str)

            # Skip if no price or out of budget
            if not price or price <= 0:
                return None

            if requirements.budget and price > requirements.budget.get_effective_max():
                if Config.DEBUG:
                    print(f"[SerpAPI] Skipping {name[:30]} - ${price} over budget")
                return None

            # Extract source/retailer
            source = item.get("source", "unknown")
            retailer = self._normalize_retailer(source)

            # Extract URL
            url = item.get("link", "")

            # Extract rating
            rating_str = item.get("rating", "0")
            rating = float(rating_str) if rating_str else 0.0

            # Extract review count
            reviews_str = item.get("reviews", "0")
            review_count = self._parse_review_count(reviews_str)

            # Generate product ID
            product_id = hashlib.md5(f"{name}{source}".encode()).hexdigest()[:16]

            # Extract manufacturer (usually first word)
            manufacturer = name.split()[0] if name else "Unknown"

            # Build product
            product = Product(
                id=product_id,
                name=name,
                manufacturer=manufacturer,
                category=requirements.product_category,
                specifications={
                    "source": source,
                    "thumbnail": item.get("thumbnail", "")
                },
                pricing={
                    retailer: PriceInfo(
                        current_price=price,
                        in_stock=True,
                        url=url,
                        last_updated=datetime.now()
                    )
                },
                reviews={
                    retailer: ReviewSummary(
                        average_rating=rating,
                        total_reviews=review_count,
                        rating_distribution={}
                    )
                },
                image_url=item.get("thumbnail"),
                scraped_at=datetime.now()
            )

            if Config.DEBUG:
                print(f"[SerpAPI] Extracted: {name[:40]} - ${price} from {source}")

            return product

        except Exception as e:
            if Config.DEBUG:
                print(f"[SerpAPI] Error extracting product: {e}")
            return None

    def _parse_price(self, price_str: str) -> float:
        """Parse price string to float."""
        if not price_str:
            return 0.0

        # Remove currency symbols and commas
        import re
        cleaned = re.sub(r'[,$€£¥]', '', str(price_str))

        # Extract first number
        match = re.search(r'(\d+\.?\d*)', cleaned)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return 0.0

        return 0.0

    def _parse_review_count(self, reviews_str: str) -> int:
        """Parse review count string to int."""
        if not reviews_str:
            return 0

        # Extract number from strings like "1,234 reviews" or "1.2K"
        import re

        # Handle K notation (1.2K -> 1200)
        if 'k' in str(reviews_str).lower():
            match = re.search(r'(\d+\.?\d*)k', str(reviews_str).lower())
            if match:
                return int(float(match.group(1)) * 1000)

        # Extract regular number
        cleaned = re.sub(r'[,\s]', '', str(reviews_str))
        match = re.search(r'(\d+)', cleaned)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return 0

        return 0

    def _normalize_retailer(self, source: str) -> str:
        """Normalize retailer name."""
        source_lower = source.lower()

        if 'amazon' in source_lower:
            return 'amazon'
        elif 'walmart' in source_lower:
            return 'walmart'
        elif 'best buy' in source_lower or 'bestbuy' in source_lower:
            return 'bestbuy'
        else:
            # Use first word of source
            return source.split()[0].lower() if source else 'unknown'
