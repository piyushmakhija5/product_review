"""
Research Agent using Perplexity's Sonar API with search.
Perplexity provides web search with LLM-powered extraction in one API call.
"""
from openai import OpenAI
from models.product import Product, PriceInfo, ReviewSummary
from models.requirements import UserRequirements
from utils.terminal import print_status, print_success, print_warning
from config import Config
from typing import List
from datetime import datetime
import json
import hashlib


class PerplexityResearcher:
    """
    Agent that uses Perplexity's Sonar API for web search and product extraction.
    Perplexity combines search + LLM analysis in one call.
    """

    def __init__(self):
        if not Config.PERPLEXITY_API_KEY:
            raise ValueError("PERPLEXITY_API_KEY is required. Get one at https://www.perplexity.ai/settings/api")

        # Perplexity API is OpenAI-compatible
        self.client = OpenAI(
            api_key=Config.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )

    def search(self, requirements: UserRequirements) -> List[Product]:
        """
        Search for products using Perplexity's search-enabled model.

        Args:
            requirements: User requirements

        Returns:
            List of Product objects
        """
        print_status("Searching via Perplexity AI...")

        try:
            products = self._search_with_perplexity(requirements)

            if products:
                print_success(f"Found {len(products)} products via Perplexity")
            else:
                print_warning("No products found")

            return products

        except Exception as e:
            print_warning(f"Search error: {str(e)}")
            if Config.DEBUG:
                import traceback
                traceback.print_exc()
            return []

    def _search_with_perplexity(self, requirements: UserRequirements) -> List[Product]:
        """Use Perplexity to search and extract product information."""

        # Build search prompt
        search_prompt = self._build_search_prompt(requirements)

        if Config.DEBUG:
            print(f"[Perplexity] Prompt: {search_prompt[:200]}...")

        try:
            # Call Perplexity with search enabled
            response = self.client.chat.completions.create(
                model="llama-3.1-sonar-large-128k-online",  # Search-enabled model
                messages=[
                    {
                        "role": "system",
                        "content": "You are a product research assistant. Search the web for products and extract accurate information."
                    },
                    {
                        "role": "user",
                        "content": search_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )

            # Extract response
            content = response.choices[0].message.content

            if Config.DEBUG:
                print(f"[Perplexity] Response length: {len(content)} chars")
                print(f"[Perplexity] Citations: {len(response.citations) if hasattr(response, 'citations') else 0}")

            # Parse products from response
            products = self._parse_products_from_response(content, requirements)

            return products

        except Exception as e:
            if Config.DEBUG:
                print(f"[Perplexity] Error: {e}")
            raise

    def _build_search_prompt(self, requirements: UserRequirements) -> str:
        """Build search prompt for Perplexity."""

        return f"""
Search the web for products that match these requirements and extract detailed information.

USER REQUIREMENTS:
{requirements.model_dump_readable()}

TASK:
Search Amazon, Walmart, Best Buy, and other major retailers for products matching these requirements.
For each product found, extract:
1. Product name (full, accurate name)
2. Current price
3. Retailer/source
4. Product URL
5. Average rating (out of 5)
6. Number of reviews
7. Key features that match the requirements

Focus on finding 5-10 products that:
- Match the product category: {requirements.product_category}
- Are within budget: ${requirements.budget.max if requirements.budget else 'any'}
- Meet the use case: {requirements.use_case}
- Have the required features: {', '.join(str(v) for v in list(requirements.must_have_specs.values())[:3]) if requirements.must_have_specs else 'none specified'}

Return the information in this JSON format:
{{
  "products": [
    {{
      "name": "Full product name",
      "price": 299.99,
      "retailer": "amazon",
      "url": "https://...",
      "rating": 4.5,
      "review_count": 1234,
      "features": ["feature1", "feature2", "feature3"],
      "in_stock": true
    }}
  ]
}}

Only include products that are currently available and match the requirements well.
Ensure all prices are within the specified budget.
"""

    def _parse_products_from_response(
        self,
        content: str,
        requirements: UserRequirements
    ) -> List[Product]:
        """Parse products from Perplexity's response."""

        products = []

        try:
            # Try to extract JSON from response
            # Perplexity might include explanatory text, so find the JSON part
            json_start = content.find('{')
            json_end = content.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = content[json_start:json_end]
                data = json.loads(json_str)

                product_list = data.get('products', [])

                if Config.DEBUG:
                    print(f"[Perplexity] Parsed {len(product_list)} products from JSON")

                for item in product_list:
                    product = self._convert_to_product(item, requirements)
                    if product:
                        products.append(product)

        except json.JSONDecodeError as e:
            if Config.DEBUG:
                print(f"[Perplexity] JSON parse error: {e}")
                print(f"[Perplexity] Content: {content[:500]}")

        return products

    def _convert_to_product(self, item: dict, requirements: UserRequirements) -> Product:
        """Convert parsed item to Product object."""

        try:
            name = item.get('name', '')
            if not name:
                return None

            price = float(item.get('price', 0))
            if price <= 0:
                return None

            # Check budget
            if requirements.budget and price > requirements.budget.get_effective_max():
                if Config.DEBUG:
                    print(f"[Perplexity] Skipping {name[:30]} - over budget")
                return None

            retailer = item.get('retailer', 'unknown').lower()
            url = item.get('url', '')
            rating = float(item.get('rating', 0))
            review_count = int(item.get('review_count', 0))
            features = item.get('features', [])
            in_stock = item.get('in_stock', True)

            # Generate product ID
            product_id = hashlib.md5(f"{name}{retailer}".encode()).hexdigest()[:16]

            # Extract manufacturer
            manufacturer = name.split()[0] if name else "Unknown"

            # Build product
            product = Product(
                id=product_id,
                name=name,
                manufacturer=manufacturer,
                category=requirements.product_category,
                specifications={
                    "features": features
                },
                pricing={
                    retailer: PriceInfo(
                        current_price=price,
                        in_stock=in_stock,
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
                scraped_at=datetime.now()
            )

            if Config.DEBUG:
                print(f"[Perplexity] Extracted: {name[:40]} - ${price} from {retailer}")

            return product

        except Exception as e:
            if Config.DEBUG:
                print(f"[Perplexity] Error converting product: {e}")
            return None
