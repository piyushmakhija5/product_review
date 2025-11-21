"""
Collector Agent - Gathers missing information from users through conversation.
"""
from utils.llm import LLMClient
from utils.terminal import console, get_input
from models.requirements import UserRequirements, PlannerDecision
from config import Config
from typing import List


class CollectorAgent:
    """
    Agent responsible for conversationally gathering missing requirement information.
    """

    def __init__(self):
        self.llm = LLMClient()
        self.system_prompt = self._load_system_prompt()
        self.conversation_history = []
        self.asked_questions = []  # Track questions we've already asked

    def _load_system_prompt(self) -> str:
        """Load system prompt from file."""
        prompt_file = Config.PROMPTS_DIR / "collector_system.txt"
        if prompt_file.exists():
            return prompt_file.read_text()
        return "You are a helpful assistant gathering product requirements."

    def gather(
        self,
        requirements: UserRequirements,
        missing_fields: List[str],
        suggested_questions: List[str] = None
    ) -> str:
        """
        Gather missing information through conversation.

        Args:
            requirements: Current requirements
            missing_fields: List of missing fields
            suggested_questions: Suggested questions from planner

        Returns:
            User's response string
        """
        # Build context for the conversation
        context = self._build_context(requirements, missing_fields, suggested_questions)

        # Generate question (avoiding duplicates)
        question = self._generate_question(context, suggested_questions, requirements)

        # Track this question
        self.asked_questions.append(question)

        # Get user response
        console.print(f"\n[bold cyan]Agent:[/bold cyan] {question}")
        user_response = get_input("You")

        return user_response

    def _build_context(
        self,
        requirements: UserRequirements,
        missing_fields: List[str],
        suggested_questions: List[str] = None
    ) -> str:
        """Build context for question generation."""
        parts = []

        parts.append("WHAT WE KNOW:")
        if requirements.product_category:
            parts.append(f"- Product: {requirements.product_category}")
        if requirements.budget:
            parts.append(f"- Budget: ${requirements.budget.max:.0f}")
        if requirements.use_case:
            parts.append(f"- Use case: {requirements.use_case}")
        if requirements.must_have_specs:
            parts.append(f"- Specs: {', '.join(f'{k}: {v}' for k, v in list(requirements.must_have_specs.items())[:3])}")

        parts.append("\nWHAT WE NEED:")
        for field in missing_fields:
            parts.append(f"- {field.replace('_', ' ').title()}")

        if suggested_questions:
            parts.append("\nSUGGESTED QUESTIONS:")
            for q in suggested_questions[:3]:
                parts.append(f"- {q}")

        return "\n".join(parts)

    def _generate_question(
        self,
        context: str,
        suggested_questions: List[str] = None,
        requirements: UserRequirements = None
    ) -> str:
        """Generate next question to ask user, avoiding duplicates."""

        # Check suggested questions first (but avoid already asked ones)
        if suggested_questions:
            for q in suggested_questions:
                # Check if we've asked something similar
                if not any(self._is_similar_question(q, asked) for asked in self.asked_questions):
                    return q

        # Generate a contextual question based on what we know
        # Build a better prompt
        known_info = []
        if requirements:
            if requirements.product_category:
                known_info.append(f"Product type: {requirements.product_category}")
            if requirements.budget:
                known_info.append(f"Budget: ${requirements.budget.max}")
            if requirements.use_case:
                known_info.append(f"Use case: {requirements.use_case}")

        prompt = f"""
{context}

We've already asked these questions:
{chr(10).join('- ' + q for q in self.asked_questions[-3:]) if self.asked_questions else '(none)'}

What we know so far:
{chr(10).join('- ' + info for info in known_info) if known_info else '(very little)'}

Generate a single, natural, conversational question to gather the MOST IMPORTANT missing information.

Guidelines:
- DO NOT repeat questions we've already asked
- Focus on what's still missing (budget, use case, key requirements)
- Be specific and helpful
- Keep it natural and conversational

Return ONLY the question, no extra text.
"""

        try:
            question = self.llm.call(
                prompt=prompt,
                system=self.system_prompt,
                temperature=0.7,
                max_tokens=200
            )
            return question.strip()

        except Exception as e:
            if Config.DEBUG:
                print(f"Question generation error: {e}")

            # Fallback based on what's missing
            if requirements:
                if not requirements.budget:
                    return "What's your budget for this purchase?"
                elif not requirements.use_case:
                    return "How do you plan to use this product?"
                elif not requirements.must_have_specs:
                    return "Are there any specific features or specs you need?"

            return "Could you tell me more about what you're looking for?"

    def _is_similar_question(self, q1: str, q2: str) -> bool:
        """Check if two questions are asking about the same thing."""
        # Simple similarity check - could be improved
        q1_lower = q1.lower()
        q2_lower = q2.lower()

        # Check for key phrases
        key_phrases = [
            'what type', 'which type', 'what kind',
            'budget', 'price', 'cost',
            'use case', 'how will you use', 'what will you use'
        ]

        for phrase in key_phrases:
            if phrase in q1_lower and phrase in q2_lower:
                return True

        return False
