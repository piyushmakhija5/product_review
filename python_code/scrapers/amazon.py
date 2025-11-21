"""
Amazon scraper for product information.

Note: Amazon has anti-scraping measures. This is a simplified implementation
for MVP purposes. In production, consider using Amazon Product Advertising API
or more sophisticated scraping techniques.
"""
from .base import BaseScraper
from models.product import Product, PriceInfo, ReviewSummary
from models.requirements import UserRequirements
from config import Config
from datetime import datetime
from typing import List, Optional
import urllib.parse


class AmazonScraper(BaseScraper):
    """Scraper for Amazon.com"""

    BASE_URL = "https://www.amazon.com"

    def __init__(self):
        super().__init__("amazon")

    def search(self, requirements: UserRequirements) -> List[Product]:
        """
        Search Amazon for products matching requirements.

        Args:
            requirements: User requirements

        Returns:
            List of Product objects
        """
        query = self.build_search_query(requirements)
        encoded_query = urllib.parse.quote_plus(query)

        # Build search URL with filters
        search_url = f"{self.BASE_URL}/s?k={encoded_query}"

        # Add price filter if budget specified
        if requirements.budget:
            # Amazon price filter format: &rh=p_36:min-max (in cents)
            max_price_cents = int(requirements.budget.get_effective_max() * 100)
            search_url += f"&rh=p_36:-{max_price_cents}"

        try:
            if Config.DEBUG:
                print(f"[Amazon] Search URL: {search_url}")
                print(f"[Amazon] Query: {query}")

            response = self.get(search_url)
            soup = self.parse_html(response.text)

            if Config.DEBUG:
                # Save HTML for debugging
                with open('debug_amazon_search.html', 'w', encoding='utf-8') as f:
                    f.write(soup.prettify())
                print(f"[Amazon] HTML saved to debug_amazon_search.html")

            products = self._extract_products(soup, requirements)

            if Config.DEBUG:
                print(f"[Amazon] Found {len(products)} products")

            return products[:Config.MAX_PRODUCTS_PER_RETAILER]

        except Exception as e:
            self.log_scrape_error(e, "search")
            if Config.DEBUG:
                import traceback
                traceback.print_exc()
            return []

    def _extract_products(self, soup, requirements: UserRequirements) -> List[Product]:
        """Extract product information from search results page."""
        products = []

        # Amazon search results are in divs with data-component-type attribute
        items = soup.select('[data-component-type="s-search-result"]')

        if Config.DEBUG:
            print(f"[Amazon] Found {len(items)} search result items in HTML")
            if len(items) == 0:
                # Try alternative selectors
                alt_items = soup.select('.s-result-item')
                print(f"[Amazon] Alternative selector found {len(alt_items)} items")

        for item in items:
            try:
                product = self._extract_product_from_item(item, requirements)
                if product:
                    products.append(product)
                elif Config.DEBUG:
                    print(f"[Amazon] Item skipped (no product extracted)")
            except Exception as e:
                self.log_scrape_error(e, "extract_product")
                if Config.DEBUG:
                    import traceback
                    traceback.print_exc()
                continue

        return products

    def _extract_product_from_item(self, item, requirements: UserRequirements) -> Optional[Product]:
        """Extract product information from a single search result item."""

        # Extract title
        title_elem = item.select_one('h2 a span')
        if not title_elem:
            return None
        name = self.clean_text(title_elem.get_text())

        # Extract price
        price_elem = item.select_one('.a-price .a-offscreen')
        if not price_elem:
            return None  # Skip products without price
        price = self.extract_price(price_elem.get_text())

        if not price or price <= 0:
            return None

        # Check budget
        if not self.is_within_budget(price, requirements):
            return None

        # Extract URL
        link_elem = item.select_one('h2 a')
        url = ""
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
            url = f"{self.BASE_URL}{href}" if href.startswith('/') else href

        # Extract rating
        rating_elem = item.select_one('.a-icon-star-small span.a-icon-alt')
        rating = 0.0
        if rating_elem:
            rating = self.extract_rating(rating_elem.get_text()) or 0.0

        # Extract review count
        review_count_elem = item.select_one('span[aria-label*="stars"] + span')
        review_count = 0
        if review_count_elem:
            review_text = review_count_elem.get_text()
            # Extract number from text like "1,234"
            review_text = review_text.replace(',', '')
            try:
                review_count = int(''.join(filter(str.isdigit, review_text)))
            except ValueError:
                review_count = 0

        # Extract brand (usually first word of title)
        brand = self.extract_brand(name)

        # Extract ASIN from URL or data attribute
        asin = self._extract_asin(item, url)

        # Generate product ID
        product_id = self.generate_product_id(name)

        # Create Product object
        product = Product(
            id=product_id,
            name=name,
            manufacturer=brand,
            model_number=asin,
            category=requirements.product_category,
            specifications={
                "asin": asin
            },
            pricing={
                "amazon": PriceInfo(
                    current_price=price,
                    in_stock=True,  # Assume in stock if it appears in search
                    url=url,
                    last_updated=datetime.now()
                )
            },
            reviews={
                "amazon": ReviewSummary(
                    average_rating=rating,
                    total_reviews=review_count,
                    rating_distribution={}
                )
            },
            scraped_at=datetime.now()
        )

        return product

    def _extract_asin(self, item, url: str) -> str:
        """Extract ASIN (Amazon Standard Identification Number) from item or URL."""
        # Try data attribute first
        asin = item.get('data-asin', '')
        if asin:
            return asin

        # Try to extract from URL
        # URL format: /dp/ASIN/ or /gp/product/ASIN/
        import re
        if url:
            match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', url)
            if match:
                return match.group(1)

        return ""

    def get_product_details(self, asin: str) -> Optional[dict]:
        """
        Get detailed product information for a specific ASIN.
        This would be used to enrich product data.

        Args:
            asin: Amazon Standard Identification Number

        Returns:
            Dict with detailed product info or None
        """
        if not asin:
            return None

        url = f"{self.BASE_URL}/dp/{asin}"

        try:
            response = self.get(url)
            soup = self.parse_html(response.text)

            details = {
                "asin": asin,
                "url": url
            }

            # Extract additional details (simplified)
            # In production, this would extract specs, description, etc.

            return details

        except Exception as e:
            self.log_scrape_error(e, f"get_details:{asin}")
            return None
