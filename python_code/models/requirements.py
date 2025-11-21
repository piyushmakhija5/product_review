"""
Pydantic models for user requirements and constraints.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from enum import Enum


class BudgetConstraint(BaseModel):
    """User's budget constraints for the product."""
    min: Optional[float] = None
    max: float
    flexible: bool = False
    flexibility_percent: Optional[float] = None

    @field_validator('max')
    @classmethod
    def validate_max(cls, v):
        if v <= 0:
            raise ValueError('Maximum budget must be positive')
        return v

    @field_validator('min')
    @classmethod
    def validate_min(cls, v, info):
        if v is not None and v < 0:
            raise ValueError('Minimum budget cannot be negative')
        return v

    def get_effective_max(self) -> float:
        """Get the effective maximum budget including flexibility."""
        if self.flexible and self.flexibility_percent:
            return self.max * (1 + self.flexibility_percent / 100)
        return self.max


class Priority(str, Enum):
    """Priority levels for requirements."""
    CRITICAL = "critical"  # Must have
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NICE_TO_HAVE = "nice_to_have"


class UserRequirements(BaseModel):
    """Complete user requirements for product search."""

    # Basic information
    product_category: str = ""
    budget: Optional[BudgetConstraint] = None
    use_case: str = ""

    # Specifications
    must_have_specs: Dict[str, Any] = Field(default_factory=dict)
    nice_to_have_specs: Dict[str, Any] = Field(default_factory=dict)
    deal_breakers: List[str] = Field(default_factory=list)

    # Preferences
    preferred_brands: List[str] = Field(default_factory=list)
    excluded_brands: List[str] = Field(default_factory=list)
    preferred_retailers: List[str] = Field(default_factory=list)

    # Priority ordering
    priorities: List[str] = Field(default_factory=list)

    # Metadata
    completeness_score: float = 0.0
    raw_input: str = ""

    def is_complete(self) -> bool:
        """
        Check if requirements are complete enough to proceed with research.

        Criteria:
        - Product category is specified
        - Budget is set
        - At least one must-have spec OR clear use case
        - Completeness score >= 0.7
        """
        has_category = bool(self.product_category and len(self.product_category) > 2)
        has_budget = self.budget is not None and self.budget.max > 0
        has_specs_or_usecase = bool(self.must_have_specs or self.use_case)
        has_good_score = self.completeness_score >= 0.7

        return has_category and has_budget and has_specs_or_usecase and has_good_score

    def get_missing_fields(self) -> List[str]:
        """Return list of missing or unclear fields."""
        missing = []

        if not self.product_category:
            missing.append("product_category")

        if not self.budget or self.budget.max <= 0:
            missing.append("budget")

        if not self.must_have_specs and not self.use_case:
            missing.append("specifications_or_use_case")

        return missing

    def to_search_query(self) -> str:
        """Generate a search query string from requirements."""
        parts = [self.product_category]

        # Add key specs
        for key, value in self.must_have_specs.items():
            if isinstance(value, (str, int, float)):
                parts.append(str(value))

        return " ".join(parts)

    def model_dump_readable(self) -> str:
        """Return a human-readable string representation."""
        lines = [
            f"Product: {self.product_category}",
        ]
        
        if self.budget:
            lines.append(f"Budget: ${self.budget.min or 0:.0f} - ${self.budget.max:.0f}")
        else:
            lines.append("Budget: Not specified")

        if self.use_case:
            lines.append(f"Use Case: {self.use_case}")

        if self.must_have_specs:
            lines.append("Must-Have Specs:")
            for key, value in self.must_have_specs.items():
                lines.append(f"  - {key}: {value}")

        if self.nice_to_have_specs:
            lines.append("Nice-to-Have:")
            for key, value in self.nice_to_have_specs.items():
                lines.append(f"  - {key}: {value}")

        if self.deal_breakers:
            lines.append("Deal Breakers:")
            for item in self.deal_breakers:
                lines.append(f"  - {item}")

        return "\n".join(lines)


class PlannerDecision(BaseModel):
    """Decision output from the Planner agent."""
    status: str  # "ready" or "need_more_info"
    missing_fields: List[str] = Field(default_factory=list)
    requirements: Optional[UserRequirements] = None
    confidence: float = 0.0
    reasoning: str = ""
    suggested_questions: List[str] = Field(default_factory=list)
