"""
Pydantic models for product data and analysis results.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class Retailer(str, Enum):
    """Supported retailers."""
    AMAZON = "amazon"
    WALMART = "walmart"
    BESTBUY = "bestbuy"


class PriceInfo(BaseModel):
    """Price information from a retailer."""
    current_price: float
    original_price: Optional[float] = None
    discount_percent: Optional[float] = None
    in_stock: bool = True
    url: str = ""
    shipping_cost: Optional[float] = None
    last_updated: datetime = Field(default_factory=datetime.now)

    @field_validator('current_price')
    @classmethod
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price cannot be negative')
        return v

    def get_total_price(self) -> float:
        """Get total price including shipping."""
        return self.current_price + (self.shipping_cost or 0)


class ReviewSummary(BaseModel):
    """Aggregated review information from a retailer."""
    average_rating: float = 0.0
    total_reviews: int = 0
    rating_distribution: Dict[str, int] = Field(default_factory=dict)  # {"5": 120, "4": 30, ...}
    common_pros: List[str] = Field(default_factory=list)
    common_cons: List[str] = Field(default_factory=list)
    recent_reviews_sample: List[str] = Field(default_factory=list)

    @field_validator('average_rating')
    @classmethod
    def validate_rating(cls, v):
        if v < 0 or v > 5:
            raise ValueError('Rating must be between 0 and 5')
        return v


class Product(BaseModel):
    """Complete product information from multiple sources."""

    # Identifiers
    id: str
    name: str
    manufacturer: str = ""
    model_number: Optional[str] = None
    category: str = ""

    # Specifications
    specifications: Dict[str, Any] = Field(default_factory=dict)

    # Pricing from different retailers
    pricing: Dict[str, PriceInfo] = Field(default_factory=dict)

    # Reviews from different retailers
    reviews: Dict[str, ReviewSummary] = Field(default_factory=dict)

    # Additional URLs
    manufacturer_url: Optional[str] = None
    image_url: Optional[str] = None

    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.now)

    def get_best_price(self) -> tuple[str, float]:
        """
        Returns (retailer, price) for best available deal.
        Only considers in-stock items.
        """
        if not self.pricing:
            return ("", 0.0)

        available = {
            retailer: price_info
            for retailer, price_info in self.pricing.items()
            if price_info.in_stock
        }

        if not available:
            return ("", 0.0)

        best = min(
            available.items(),
            key=lambda x: x[1].get_total_price()
        )

        return best[0], best[1].current_price

    def get_average_rating(self) -> float:
        """Calculate average rating across all retailers."""
        if not self.reviews:
            return 0.0

        ratings = [r.average_rating for r in self.reviews.values() if r.total_reviews > 0]
        return sum(ratings) / len(ratings) if ratings else 0.0

    def get_total_reviews(self) -> int:
        """Get total number of reviews across all retailers."""
        return sum(r.total_reviews for r in self.reviews.values())

    def get_price_range(self) -> tuple[float, float]:
        """Get min and max prices across retailers."""
        if not self.pricing:
            return (0.0, 0.0)

        prices = [p.current_price for p in self.pricing.values() if p.in_stock]
        if not prices:
            return (0.0, 0.0)

        return (min(prices), max(prices))

    def is_available(self) -> bool:
        """Check if product is available at any retailer."""
        return any(p.in_stock for p in self.pricing.values())

    def get_retailer_urls(self) -> Dict[str, str]:
        """Get URLs for all retailers."""
        return {
            retailer: price_info.url
            for retailer, price_info in self.pricing.items()
            if price_info.url
        }


class AnalysisResult(BaseModel):
    """Analysis result for a single product."""

    product: Product
    match_score: float  # 0-100 score for how well it matches requirements
    rank: int = 0

    # Requirement matching
    requirement_fulfillment: Dict[str, bool] = Field(default_factory=dict)
    missing_requirements: List[str] = Field(default_factory=list)
    exceeded_requirements: List[str] = Field(default_factory=list)

    # Value analysis
    value_score: float = 0.0  # Price to features ratio
    price_rank: int = 0

    # Review-based insights
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    common_issues: List[str] = Field(default_factory=list)

    # Unknown unknowns
    unknown_unknowns: List[str] = Field(default_factory=list)
    considerations: List[str] = Field(default_factory=list)

    # Confidence
    confidence_rating: float = 0.0  # 0-1 confidence in this analysis

    @field_validator('match_score', 'value_score')
    @classmethod
    def validate_score(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Score must be between 0 and 100')
        return v

    @field_validator('confidence_rating')
    @classmethod
    def validate_confidence(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Confidence must be between 0 and 1')
        return v


class ComparisonReport(BaseModel):
    """Final comparison report with top products."""

    # Top products
    top_products: List[AnalysisResult] = Field(default_factory=list)

    # Overall insights
    category_insights: List[str] = Field(default_factory=list)
    market_trends: List[str] = Field(default_factory=list)

    # Recommendations
    recommended_product: Optional[AnalysisResult] = None
    recommendation_reasoning: str = ""

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    total_products_analyzed: int = 0
    requirements_used: Optional[Any] = None  # UserRequirements

    def get_report_markdown(self) -> str:
        """Generate markdown report."""
        # This will be implemented in the analyzer agent
        return ""
