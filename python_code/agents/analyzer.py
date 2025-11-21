"""
Analyzer Agent - Analyzes products and generates recommendations report.
"""
from utils.llm import LLMClient
from models.product import Product, AnalysisResult, ComparisonReport
from models.requirements import UserRequirements
from config import Config
from typing import List
import json
from datetime import datetime


class AnalyzerAgent:
    """
    Agent responsible for analyzing products and generating comparison reports.
    """

    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load system prompt from file."""
        prompt_file = Config.PROMPTS_DIR / "analyzer_system.txt"
        if prompt_file.exists():
            return prompt_file.read_text()
        return "You are an expert electronics analyst."

    def analyze_and_report(
        self,
        products: List[Product],
        requirements: UserRequirements
    ) -> str:
        """
        Analyze products and generate a comprehensive report.

        Args:
            products: List of products to analyze
            requirements: User requirements

        Returns:
            Markdown formatted report
        """
        if not products:
            return self._generate_no_products_report(requirements)

        # Prepare product data for LLM
        product_data = self._prepare_product_data(products)

        # Build analysis prompt
        prompt = self._build_analysis_prompt(product_data, requirements)

        # Call LLM with extended thinking
        try:
            # Note: Claude requires temperature=1.0 when thinking is enabled
            report = self.llm.call(
                prompt=prompt,
                system=self.system_prompt,
                thinking=True,  # Enable deep analysis
                temperature=1.0,  # Required for Claude's extended thinking
                max_tokens=4096
            )

            return report

        except Exception as e:
            if Config.DEBUG:
                print(f"Analysis error: {e}")

            # Fallback: Generate basic report
            return self._generate_fallback_report(products, requirements)

    def _prepare_product_data(self, products: List[Product]) -> str:
        """Prepare product data in a structured format for LLM."""
        lines = []

        for i, product in enumerate(products, 1):
            lines.append(f"\n{'='*60}")
            lines.append(f"PRODUCT {i}: {product.name}")
            lines.append(f"{'='*60}")

            # Basic info
            lines.append(f"Manufacturer: {product.manufacturer}")
            if product.model_number:
                lines.append(f"Model: {product.model_number}")

            # Pricing
            lines.append("\nPRICING:")
            for retailer, price_info in product.pricing.items():
                stock_status = "In Stock" if price_info.in_stock else "Out of Stock"
                lines.append(f"  {retailer.title()}: ${price_info.current_price:.2f} ({stock_status})")

            best_retailer, best_price = product.get_best_price()
            if best_retailer:
                lines.append(f"  Best Price: ${best_price:.2f} at {best_retailer.title()}")

            # Ratings
            lines.append("\nRATINGS:")
            for retailer, review in product.reviews.items():
                if review.total_reviews > 0:
                    lines.append(
                        f"  {retailer.title()}: {review.average_rating:.1f}/5 "
                        f"({review.total_reviews} reviews)"
                    )

            avg_rating = product.get_average_rating()
            if avg_rating > 0:
                lines.append(f"  Average Rating: {avg_rating:.1f}/5")

            # Specifications
            if product.specifications:
                lines.append("\nSPECIFICATIONS:")
                for key, value in product.specifications.items():
                    if key != 'asin':  # Skip technical IDs
                        lines.append(f"  {key}: {value}")

            # URLs
            lines.append("\nWHERE TO BUY:")
            for retailer, url in product.get_retailer_urls().items():
                lines.append(f"  {retailer.title()}: {url[:80]}...")

        return "\n".join(lines)

    def _build_analysis_prompt(self, product_data: str, requirements: UserRequirements) -> str:
        """Build the analysis prompt for the LLM."""
        return f"""
Analyze these electronics products and generate a comprehensive recommendation report.

USER REQUIREMENTS:
{requirements.model_dump_readable()}

PRODUCTS TO ANALYZE:
{product_data}

YOUR TASK:
1. Analyze each product against the user's requirements
2. Score each product (0-100) based on requirement match, value, and reviews
3. Identify the TOP 5 products
4. For each top product, provide:
   - Overall match score and why
   - Key specifications compared to requirements
   - Pros and cons
   - Unknown unknowns (important considerations the user might miss)
   - Price comparison across retailers
5. Create a comparison matrix of top 5 products
6. Provide your FINAL RECOMMENDATION with clear reasoning
7. Include actionable next steps for the user

IMPORTANT - Unknown Unknowns:
Look for and surface:
- Common complaints in reviews that aren't obvious from specs
- Compatibility issues
- Hidden costs
- Software/firmware support concerns
- Better alternatives coming soon
- Category-specific gotchas

FORMAT:
Generate a well-structured markdown report with clear sections.
Use tables where appropriate.
Be specific and actionable.
Focus on helping the user make the best decision.

Think deeply about trade-offs and long-term satisfaction.
"""

    def _generate_no_products_report(self, requirements: UserRequirements) -> str:
        """Generate report when no products were found."""
        return f"""
# Product Research Report

## Your Requirements
{requirements.model_dump_readable()}

## Results

Unfortunately, no products were found matching your criteria.

### Suggestions:
1. **Increase Budget**: Your budget might be too restrictive for this category
2. **Broaden Search**: Consider relaxing some specifications
3. **Check Availability**: Some products might be temporarily out of stock
4. **Different Category**: Consider related product categories

### Next Steps:
1. Review your requirements and adjust if needed
2. Try searching with fewer restrictions
3. Check back later as inventory changes frequently
"""

    def _generate_fallback_report(self, products: List[Product], requirements: UserRequirements) -> str:
        """Generate a basic report when LLM analysis fails."""
        # Sort by rating and price
        sorted_products = sorted(
            products,
            key=lambda p: (p.get_average_rating(), -p.get_best_price()[1]),
            reverse=True
        )[:5]

        lines = [
            "# Product Research Report",
            "",
            "## Your Requirements",
            requirements.model_dump_readable(),
            "",
            "## Top 5 Recommendations",
            ""
        ]

        for i, product in enumerate(sorted_products, 1):
            retailer, price = product.get_best_price()
            rating = product.get_average_rating()

            lines.extend([
                f"### {i}. {product.name}",
                f"**Best Price:** ${price:.2f} at {retailer.title()}",
                f"**Rating:** {rating:.1f}/5",
                "",
                "**Where to Buy:**"
            ])

            for ret, url in product.get_retailer_urls().items():
                lines.append(f"- [{ret.title()}]({url})")

            lines.append("")

        return "\n".join(lines)
