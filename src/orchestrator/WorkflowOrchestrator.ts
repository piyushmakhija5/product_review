/**
 * Workflow Orchestrator - Coordinates all agents in sequence
 * Simple but robust orchestration with error handling
 */

import { PlannerAgent, UserRequirements, ChatResponse } from "../agents/PlannerAgent";
import { ResearchAgent, ResearchResults } from "../agents/ResearchAgent";
import { AnalyzerAgent, AnalysisReport } from "../agents/AnalyzerAgent";

export interface WorkflowResult {
  success: boolean;
  requirements?: UserRequirements;
  researchResults?: ResearchResults;
  analysisReport?: AnalysisReport;
  formattedReport?: string;
  error?: string;
}

export class WorkflowOrchestrator {
  private planner: PlannerAgent;
  private researcher: ResearchAgent;
  private analyzer: AnalyzerAgent;
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
    this.planner = new PlannerAgent(apiKey);
    this.researcher = new ResearchAgent(apiKey);
    this.analyzer = new AnalyzerAgent(apiKey);
  }

  /**
   * Run the complete workflow with a callback for each user interaction
   */
  async runWorkflow(
    onUserPrompt: () => Promise<string>,
    onMessage: (message: string) => void
  ): Promise<WorkflowResult> {
    try {
      // Phase 1: Planning - Collect requirements
      onMessage("\n🎯 Phase 1: Understanding Your Needs\n");

      const requirements = await this.collectRequirements(onUserPrompt, onMessage);

      if (!requirements) {
        return {
          success: false,
          error: "Failed to collect requirements",
        };
      }

      onMessage("\n✅ Requirements collected successfully!\n");

      // Phase 2: Research - Find products
      onMessage("\n🔍 Phase 2: Researching Products\n");
      onMessage("This may take a minute as we search the web...\n");

      const researchResults = await this.conductResearch(requirements, onMessage);

      if (!researchResults || researchResults.products_found.length === 0) {
        return {
          success: false,
          requirements,
          error: "No products found matching your requirements",
        };
      }

      onMessage(
        `\n✅ Found ${researchResults.products_found.length} products to analyze!\n`
      );

      // Phase 3: Analysis - Generate report
      onMessage("\n📊 Phase 3: Analyzing Products & Generating Report\n");

      const analysisReport = await this.analyzeProducts(
        requirements,
        researchResults,
        onMessage
      );

      if (!analysisReport) {
        return {
          success: false,
          requirements,
          researchResults,
          error: "Failed to generate analysis report",
        };
      }

      // Format the final report
      const formattedReport = this.analyzer.formatReportForDisplay(analysisReport);

      onMessage("\n✅ Analysis complete!\n");

      return {
        success: true,
        requirements,
        researchResults,
        analysisReport,
        formattedReport,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      onMessage(`\n❌ Workflow error: ${errorMessage}\n`);

      return {
        success: false,
        error: errorMessage,
      };
    }
  }

  /**
   * Phase 1: Collect requirements from user
   */
  private async collectRequirements(
    onUserPrompt: () => Promise<string>,
    onMessage: (message: string) => void
  ): Promise<UserRequirements | null> {
    try {
      let isComplete = false;
      let chatResponse: ChatResponse | null = null;

      // Get initial input
      const initialInput = await onUserPrompt();

      if (!initialInput || initialInput.trim().length === 0) {
        onMessage("❌ Please provide some details about what you're looking for.\n");
        return null;
      }

      // Start conversation
      chatResponse = await this.planner.chat(initialInput);
      onMessage(`\n${chatResponse.conversation}\n`);

      isComplete = chatResponse.isComplete;

      // Continue conversation until complete (max 5 rounds to prevent infinite loop)
      let roundCount = 1;
      const maxRounds = 5;

      while (!isComplete && roundCount < maxRounds) {
        const userResponse = await onUserPrompt();

        if (!userResponse || userResponse.trim().length === 0) {
          onMessage("❌ Please provide a response.\n");
          continue;
        }

        // Check for exit commands
        if (["quit", "exit", "cancel"].includes(userResponse.toLowerCase())) {
          onMessage("👋 Cancelled. Goodbye!\n");
          return null;
        }

        chatResponse = await this.planner.chat(userResponse);
        onMessage(`\n${chatResponse.conversation}\n`);

        isComplete = chatResponse.isComplete;
        roundCount++;
      }

      // Force completion if we've hit max rounds and have basic info
      if (!isComplete && roundCount >= maxRounds) {
        const requirements = this.planner.getFinalRequirements();
        if (requirements.product_type && requirements.budget_max) {
          onMessage(
            "\n⚠️  Moving forward with what we have. We can refine later!\n"
          );
          isComplete = true;
        }
      }

      if (!isComplete) {
        onMessage("❌ Unable to gather enough information. Please try again.\n");
        return null;
      }

      return this.planner.getFinalRequirements();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      onMessage(`❌ Error collecting requirements: ${errorMessage}\n`);
      return null;
    }
  }

  /**
   * Phase 2: Research products based on requirements
   */
  private async conductResearch(
    requirements: UserRequirements,
    onMessage: (message: string) => void
  ): Promise<ResearchResults | null> {
    try {
      const results = await this.researcher.research(requirements);

      // Validate results
      if (!results || !results.products_found) {
        throw new Error("Invalid research results");
      }

      return results;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      onMessage(`❌ Research error: ${errorMessage}\n`);
      return null;
    }
  }

  /**
   * Phase 3: Analyze products and generate report
   */
  private async analyzeProducts(
    requirements: UserRequirements,
    researchResults: ResearchResults,
    onMessage: (message: string) => void
  ): Promise<AnalysisReport | null> {
    try {
      const maxProducts = 5;
      const report = await this.analyzer.analyzeProducts(
        requirements,
        researchResults,
        maxProducts
      );

      // Validate report
      if (!report || !report.products) {
        throw new Error("Invalid analysis report");
      }

      return report;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      onMessage(`❌ Analysis error: ${errorMessage}\n`);
      return null;
    }
  }

  /**
   * Reset all agents for a new workflow
   */
  reset(): void {
    this.planner.reset();
    // Research and Analyzer agents don't maintain state, so no reset needed
  }
}
