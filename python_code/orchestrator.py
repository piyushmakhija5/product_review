"""
Main orchestrator that coordinates all agents to complete the workflow.
"""
from agents.planner import PlannerAgent
from agents.collector import CollectorAgent
from agents.researcher_serp import SerpAPIResearcher
from agents.researcher_perplexity import PerplexityResearcher
from agents.analyzer import AnalyzerAgent
from models.requirements import UserRequirements
from utils.terminal import (
    print_header, print_status, print_success, print_error,
    print_requirements_summary, print_markdown, show_progress,
    save_report_prompt
)
from config import Config
from datetime import datetime
from pathlib import Path


class WorkflowOrchestrator:
    """
    Orchestrates the complete workflow from requirements gathering to report generation.
    """

    def __init__(self):
        self.planner = PlannerAgent()
        self.collector = CollectorAgent()

        # Choose researcher based on SEARCH_PROVIDER config
        if Config.SEARCH_PROVIDER == 'perplexity':
            self.researcher = PerplexityResearcher()
        elif Config.SEARCH_PROVIDER == 'serpapi':
            self.researcher = SerpAPIResearcher()
        else:
            raise ValueError(
                f"Invalid SEARCH_PROVIDER: {Config.SEARCH_PROVIDER}. "
                f"Must be 'serpapi' or 'perplexity'"
            )

        self.analyzer = AnalyzerAgent()

    def run(self, initial_input: str) -> str:
        """
        Execute the complete workflow.

        Args:
            initial_input: Initial user input describing what they want

        Returns:
            Generated report as markdown string
        """
        try:
            # Phase 1: Requirement Analysis and Collection
            requirements = self._gather_requirements(initial_input)

            if not requirements or not requirements.is_complete():
                print_error("Failed to gather complete requirements")
                return ""

            # Phase 2: Product Research
            products = self._research_products(requirements)

            if not products:
                print_error("No products found matching your requirements")
                return self._generate_no_results_report(requirements)

            # Phase 3: Analysis and Report Generation
            report = self._analyze_and_report(products, requirements)

            # Phase 4: Save Report
            if Config.SAVE_REPORTS:
                self._save_report(report, requirements)

            return report

        except KeyboardInterrupt:
            print_error("\nWorkflow interrupted by user")
            return ""
        except Exception as e:
            print_error(f"Workflow error: {str(e)}")
            if Config.DEBUG:
                raise
            return ""

    def _gather_requirements(self, initial_input: str) -> UserRequirements:
        """
        Gather complete user requirements through planning and collection.

        Args:
            initial_input: Initial user input

        Returns:
            Complete UserRequirements object
        """
        print_header("Phase 1: Understanding Your Needs")

        # Build conversation history
        conversation_history = [initial_input]

        # Initial analysis
        print_status("Analyzing your requirements...")
        decision = self.planner.analyze(initial_input)

        if Config.DEBUG:
            print(f"[DEBUG] Initial decision status: {decision.status}")
            print(f"[DEBUG] Missing fields: {decision.missing_fields}")
            print(f"[DEBUG] Completeness: {decision.confidence}")

        requirements = decision.requirements or UserRequirements(raw_input=initial_input)

        # Collect more information if needed
        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while decision.status == "need_more_info" and iteration < max_iterations:
            iteration += 1

            if Config.DEBUG:
                print(f"\n[DEBUG] Iteration {iteration}")
                print(f"[DEBUG] Current requirements: {requirements.model_dump_readable()}")
                print(f"[DEBUG] Missing: {decision.missing_fields}")

            print_status(f"\nI need more details ({iteration}/{max_iterations})...")

            # Show what's missing
            if decision.missing_fields:
                print_status(f"Missing: {', '.join(decision.missing_fields)}")

            # Get next piece of information
            user_response = self.collector.gather(
                requirements,
                decision.missing_fields,
                decision.suggested_questions
            )

            if not user_response or user_response.lower() in ['quit', 'exit', 'cancel']:
                print_error("Requirement gathering cancelled")
                return None

            # Add to conversation history
            conversation_history.append(user_response)

            # Build full context from conversation
            full_context = "\n\n".join([
                f"User: {msg}" for msg in conversation_history
            ])

            if Config.DEBUG:
                print(f"[DEBUG] User response: {user_response}")

            # Update requirements with new information
            requirements = self.planner.update_requirements(requirements, user_response)

            if Config.DEBUG:
                print(f"[DEBUG] Updated requirements completeness: {requirements.completeness_score}")

            # Re-analyze with full context and updated requirements
            decision = self.planner.analyze(full_context, requirements)

            # Update requirements from decision
            if decision.requirements:
                requirements = decision.requirements

            if Config.DEBUG:
                print(f"[DEBUG] New decision status: {decision.status}")
                print(f"[DEBUG] New completeness: {decision.confidence}")

            # Check if we're making progress
            if iteration > 1 and decision.status == "need_more_info":
                # If completeness score is high enough, force completion
                if requirements.completeness_score >= 0.7:
                    if Config.DEBUG:
                        print("[DEBUG] Forcing completion - score high enough")
                    break

        # Final check
        if not requirements.is_complete():
            print_error("Unable to gather complete requirements")
            print_error(f"Missing: {', '.join(requirements.get_missing_fields())}")
            if Config.DEBUG:
                print(f"[DEBUG] Requirements state: {requirements.model_dump_json(indent=2)}")
            return None

        # Show summary
        print_success("\nRequirements gathered successfully!")
        print_header("Your Requirements Summary")
        print_requirements_summary(requirements)

        return requirements

    def _research_products(self, requirements: UserRequirements) -> list:
        """
        Research products across retailers.

        Args:
            requirements: User requirements

        Returns:
            List of products
        """
        print_header("Phase 2: Researching Products")
        print_status("This may take a few minutes as we search across multiple retailers...")

        with show_progress("Searching retailers..."):
            products = self.researcher.search(requirements)

        if products:
            print_success(f"\nFound {len(products)} products to analyze")
        else:
            print_error("\nNo products found matching your criteria")

        return products

    def _analyze_and_report(self, products: list, requirements: UserRequirements) -> str:
        """
        Analyze products and generate report.

        Args:
            products: List of products
            requirements: User requirements

        Returns:
            Report as markdown string
        """
        print_header("Phase 3: Analyzing Products")
        print_status("Using AI to deeply analyze products and generate recommendations...")

        with show_progress("Analyzing and generating report..."):
            report = self.analyzer.analyze_and_report(products, requirements)

        print_success("\nAnalysis complete!")

        return report

    def _save_report(self, report: str, requirements: UserRequirements) -> bool:
        """
        Save report to file.

        Args:
            report: Report content
            requirements: User requirements

        Returns:
            True if saved successfully
        """
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        category = requirements.product_category.replace(" ", "_")[:30]
        filename = f"report_{category}_{timestamp}.md"
        filepath = Config.REPORTS_DIR / filename

        return save_report_prompt(report, str(filepath))

    def _generate_no_results_report(self, requirements: UserRequirements) -> str:
        """Generate a report when no products are found."""
        return f"""
# Product Research Report - No Results

## Your Requirements
{requirements.model_dump_readable()}

## Results
Unfortunately, we couldn't find any products matching your specific criteria.

## Possible Reasons:
1. **Budget constraints**: Your budget might be too restrictive for this category
2. **Specific requirements**: The combination of requirements might be too specific
3. **Temporary availability**: Products might be out of stock across all retailers
4. **Search limitations**: Our search might need refinement

## Suggestions:
1. Try increasing your budget by 10-20%
2. Relax some of the nice-to-have requirements
3. Consider alternative product categories
4. Check back in a few days as inventory updates

## Next Steps:
Feel free to run the search again with adjusted requirements.
"""
