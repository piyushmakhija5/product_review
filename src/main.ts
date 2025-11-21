#!/usr/bin/env node
/**
 * Product Review Agent - Main CLI Entry Point
 * Simple command-line interface for the product review workflow
 */

import * as readline from "readline";
import * as dotenv from "dotenv";
import { WorkflowOrchestrator } from "./orchestrator/WorkflowOrchestrator";

// Load environment variables
dotenv.config();

// ANSI color codes for better CLI experience
const colors = {
  reset: "\x1b[0m",
  bright: "\x1b[1m",
  dim: "\x1b[2m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  cyan: "\x1b[36m",
};

class ProductReviewCLI {
  private rl: readline.Interface;
  private orchestrator: WorkflowOrchestrator | null = null;

  constructor() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });
  }

  /**
   * Print colored message
   */
  private print(message: string, color?: keyof typeof colors): void {
    if (color && colors[color]) {
      console.log(colors[color] + message + colors.reset);
    } else {
      console.log(message);
    }
  }

  /**
   * Print welcome banner
   */
  private printWelcome(): void {
    console.clear();
    this.print("\n" + "=".repeat(70), "cyan");
    this.print("         🛍️  ELECTRONICS PRODUCT REVIEW ASSISTANT  🛍️", "bright");
    this.print("=".repeat(70), "cyan");
    this.print("\nWelcome! I'll help you find the perfect electronics product.", "dim");
    this.print("Just tell me what you're looking for and I'll do the research!\n", "dim");
  }

  /**
   * Prompt user for input
   */
  private async getUserInput(prompt: string = "You"): Promise<string> {
    return new Promise((resolve) => {
      this.rl.question(`${colors.green}${prompt}:${colors.reset} `, (answer) => {
        resolve(answer.trim());
      });
    });
  }

  /**
   * Validate API keys
   */
  private validateApiKey(): string | null {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    const parallelKey = process.env.PARALLEL_API_KEY;

    if (!apiKey || apiKey.trim().length === 0) {
      this.print("\n❌ ERROR: ANTHROPIC_API_KEY not found!", "red");
      this.print("\nPlease set your API keys in one of these ways:", "yellow");
      this.print("1. Create a .env file with:");
      this.print("   ANTHROPIC_API_KEY=your-key-here");
      this.print("   PARALLEL_API_KEY=your-parallel-key-here");
      this.print("2. Export them:");
      this.print("   export ANTHROPIC_API_KEY=your-key-here");
      this.print("   export PARALLEL_API_KEY=your-parallel-key-here\n");
      return null;
    }

    if (!parallelKey || parallelKey.trim().length === 0) {
      this.print("\n❌ ERROR: PARALLEL_API_KEY not found!", "red");
      this.print("\nParallel AI key is required for web search functionality.", "yellow");
      this.print("Get your key from: https://parallel.ai\n");
      this.print("Add it to your .env file: PARALLEL_API_KEY=your-parallel-key-here\n");
      return null;
    }

    return apiKey;
  }

  /**
   * Main application flow
   */
  async run(): Promise<void> {
    this.printWelcome();

    // Validate API key
    const apiKey = this.validateApiKey();
    if (!apiKey) {
      this.rl.close();
      process.exit(1);
    }

    // Initialize orchestrator
    this.orchestrator = new WorkflowOrchestrator(apiKey);

    try {
      // Get initial user input
      this.print("Tell me what electronics product you're looking for:", "bright");
      this.print('(Example: "I need a gaming laptop under $1500")\n', "dim");

      // Run the workflow
      const result = await this.orchestrator.runWorkflow(
        // Callback to get user input
        async () => {
          return await this.getUserInput();
        },
        // Callback to display messages
        (message: string) => {
          // Color-code different message types
          if (message.includes("❌")) {
            this.print(message, "red");
          } else if (message.includes("✅")) {
            this.print(message, "green");
          } else if (message.includes("⚠️")) {
            this.print(message, "yellow");
          } else if (message.includes("Phase")) {
            this.print(message, "cyan");
          } else {
            console.log(message);
          }
        }
      );

      // Display results
      if (result.success && result.formattedReport) {
        this.print("\n" + "=".repeat(70), "cyan");
        this.print("                    📋 YOUR REPORT", "bright");
        this.print("=".repeat(70), "cyan");
        console.log("\n" + result.formattedReport);

        // Offer to save report
        await this.offerSaveReport(result.formattedReport);
      } else {
        this.print("\n❌ Workflow failed: " + (result.error || "Unknown error"), "red");
        this.print("\nPlease try again with different inputs.\n", "yellow");
      }

      // Ask if user wants to start over
      await this.askForRestart();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      this.print(`\n❌ Unexpected error: ${errorMessage}`, "red");
      this.print("\nPlease try again.\n", "yellow");
    } finally {
      this.rl.close();
    }
  }

  /**
   * Offer to save report to file
   */
  private async offerSaveReport(report: string): Promise<void> {
    this.print("\n" + "-".repeat(70), "dim");
    const saveResponse = await this.getUserInput(
      "Would you like to save this report? (yes/no)"
    );

    if (saveResponse.toLowerCase() === "yes" || saveResponse.toLowerCase() === "y") {
      const fs = await import("fs");
      const path = await import("path");

      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      const filename = `product-report-${timestamp}.txt`;
      const filepath = path.join(process.cwd(), filename);

      try {
        fs.writeFileSync(filepath, report, "utf-8");
        this.print(`\n✅ Report saved to: ${filename}`, "green");
      } catch (error) {
        this.print(`\n❌ Failed to save report: ${error}`, "red");
      }
    }
  }

  /**
   * Ask if user wants to restart
   */
  private async askForRestart(): Promise<void> {
    this.print("\n" + "-".repeat(70), "dim");
    const restartResponse = await this.getUserInput(
      "Would you like to search for another product? (yes/no)"
    );

    if (restartResponse.toLowerCase() === "yes" || restartResponse.toLowerCase() === "y") {
      if (this.orchestrator) {
        this.orchestrator.reset();
      }
      console.clear();
      await this.run();
    } else {
      this.print("\n👋 Thanks for using Product Review Assistant! Goodbye!\n", "cyan");
    }
  }
}

// Run the CLI application
const cli = new ProductReviewCLI();

cli.run().catch((error) => {
  console.error("\n❌ Fatal error:", error);
  process.exit(1);
});
