"""
Planner Agent - Analyzes user requirements and decides if we have enough information.
"""
from utils.llm import LLMClient
from models.requirements import UserRequirements, PlannerDecision, BudgetConstraint
from config import Config
from typing import Dict, Any
import json


class PlannerAgent:
    """
    Agent responsible for analyzing user input and determining requirement completeness.
    """

    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load system prompt from file."""
        prompt_file = Config.PROMPTS_DIR / "planner_system.txt"
        if prompt_file.exists():
            return prompt_file.read_text()
        return "You are a requirement analysis expert for electronics purchases."

    def analyze(self, user_input: str, existing_requirements: UserRequirements = None) -> PlannerDecision:
        """
        Analyze user input and determine if we have enough information.

        Args:
            user_input: Raw user input
            existing_requirements: Previously collected requirements (if any)

        Returns:
            PlannerDecision with status and extracted requirements
        """
        # Build context
        context = self._build_context(user_input, existing_requirements)

        # Define expected JSON schema
        schema = {
            "status": "ready or need_more_info",
            "missing_fields": ["list", "of", "missing", "fields"],
            "extracted_requirements": {
                "product_category": "string",
                "budget": {"min": "float or null", "max": "float", "flexible": "bool"},
                "use_case": "string",
                "must_have_specs": {"key": "value"},
                "nice_to_have_specs": {"key": "value"},
                "deal_breakers": ["list"],
                "preferred_brands": ["list"],
                "excluded_brands": ["list"]
            },
            "completeness_score": "0.0 to 1.0",
            "reasoning": "brief explanation",
            "suggested_questions": ["questions to ask if need_more_info"]
        }

        prompt = f"""
Analyze the following user input for electronics purchase requirements.

USER INPUT:
{context}

Extract all available information and determine if we have enough to proceed with product research.

Remember:
- We need: product category, budget, and either specs or use case
- Completeness score >= 0.7 means we're ready
- Be thoughtful about implicit information
- Suggest specific, helpful questions if more info is needed

Return your analysis as JSON.
"""

        try:
            # Call LLM with thinking enabled
            # Note: Claude requires temperature=1.0 when thinking is enabled
            result = self.llm.structured_output(
                prompt=prompt,
                system=self.system_prompt,
                schema=schema,
                thinking=True,
                temperature=1.0  # Required for Claude's extended thinking
            )

            if Config.DEBUG:
                print(f"[DEBUG] LLM result: {json.dumps(result, indent=2)}")

            decision = self._parse_decision(result, user_input)

            if Config.DEBUG:
                print(f"[DEBUG] Parsed decision: status={decision.status}, confidence={decision.confidence}")
                if decision.requirements:
                    print(f"[DEBUG] Requirements: category={decision.requirements.product_category}, budget={decision.requirements.budget}")

            return decision

        except Exception as e:
            if Config.DEBUG:
                print(f"[DEBUG] Planner error: {e}")
                import traceback
                traceback.print_exc()

            # Don't use fallback - raise the error so we can see what's wrong
            raise RuntimeError(f"Failed to analyze requirements: {str(e)}")

    def _build_context(self, user_input: str, existing_requirements: UserRequirements = None) -> str:
        """Build context string from user input and existing requirements."""
        parts = [f"Current input: {user_input}"]

        if existing_requirements:
            parts.append("\nPreviously collected information:")
            parts.append(existing_requirements.model_dump_readable())

        return "\n".join(parts)

    def _parse_decision(self, result: Dict[str, Any], raw_input: str) -> PlannerDecision:
        """Parse LLM result into PlannerDecision object."""
        try:
            # Extract requirements
            req_data = result.get("extracted_requirements", {})

            # Build budget
            budget = None
            if req_data.get("budget"):
                budget_data = req_data["budget"]
                if isinstance(budget_data, dict) and budget_data.get("max"):
                    budget = BudgetConstraint(
                        min=budget_data.get("min"),
                        max=budget_data.get("max", 0),
                        flexible=budget_data.get("flexible", False)
                    )

            # Build requirements
            requirements = UserRequirements(
                product_category=req_data.get("product_category", ""),
                budget=budget,
                use_case=req_data.get("use_case", ""),
                must_have_specs=req_data.get("must_have_specs", {}),
                nice_to_have_specs=req_data.get("nice_to_have_specs", {}),
                deal_breakers=req_data.get("deal_breakers", []),
                preferred_brands=req_data.get("preferred_brands", []),
                excluded_brands=req_data.get("excluded_brands", []),
                completeness_score=result.get("completeness_score", 0.0),
                raw_input=raw_input
            )

            # Build decision
            decision = PlannerDecision(
                status=result.get("status", "need_more_info"),
                missing_fields=result.get("missing_fields", []),
                requirements=requirements,
                confidence=result.get("completeness_score", 0.0),
                reasoning=result.get("reasoning", ""),
                suggested_questions=result.get("suggested_questions", [])
            )

            return decision

        except Exception as e:
            if Config.DEBUG:
                print(f"Parse error: {e}")
                print(f"Result: {json.dumps(result, indent=2)}")

            # Return minimal valid decision
            return PlannerDecision(
                status="need_more_info",
                missing_fields=["unknown"],
                confidence=0.0,
                reasoning="Failed to parse requirements",
                suggested_questions=["Could you provide more details about what you're looking for?"]
            )

    def update_requirements(
        self,
        current: UserRequirements,
        new_info: str
    ) -> UserRequirements:
        """
        Update existing requirements with new information from user.

        Args:
            current: Current requirements
            new_info: New information from user

        Returns:
            Updated requirements
        """
        # Analyze new info in context of existing requirements
        decision = self.analyze(new_info, current)

        if decision.requirements:
            # Merge with existing requirements
            merged = self._merge_requirements(current, decision.requirements)
            return merged

        return current

    def _merge_requirements(
        self,
        existing: UserRequirements,
        new: UserRequirements
    ) -> UserRequirements:
        """Merge two requirements objects, preferring non-empty values from new."""

        return UserRequirements(
            product_category=new.product_category or existing.product_category,
            budget=new.budget or existing.budget,
            use_case=new.use_case or existing.use_case,
            must_have_specs={**existing.must_have_specs, **new.must_have_specs},
            nice_to_have_specs={**existing.nice_to_have_specs, **new.nice_to_have_specs},
            deal_breakers=list(set(existing.deal_breakers + new.deal_breakers)),
            preferred_brands=list(set(existing.preferred_brands + new.preferred_brands)),
            excluded_brands=list(set(existing.excluded_brands + new.excluded_brands)),
            priorities=new.priorities or existing.priorities,
            completeness_score=max(existing.completeness_score, new.completeness_score),
            raw_input=f"{existing.raw_input}\n{new.raw_input}".strip()
        )

