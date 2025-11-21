/**
 * Analyzer Agent - Product Analysis and Report Generation
 * - Analyzes research data against user requirements
 * - Generates consumer-friendly comparison reports with ratings
 * - Identifies unknown unknowns
 * - Provides clear recommendations
 */

import Anthropic from "@anthropic-ai/sdk";
import { UserRequirements } from "./PlannerAgent";
import { ResearchResults, ProductInfo } from "./ResearchAgent";

export interface ProductRatings {
  value_for_money: number;
  performance: number;
  build_quality: number;
  user_reviews: number;
}

export interface AnalyzedProduct {
  rank: number;
  name: string;
  price: string;
  overall_rating: number;
  match_score: number;
  pros: string[];
  cons: string[];
  key_specs: Record<string, any>;
  ratings: ProductRatings;
  why_this_product: string;
  best_for: string;
}

export interface UnknownUnknownAnalysis {
  factor: string;
  why_it_matters: string;
  impact: string;
}

export interface FinalRecommendation {
  top_pick: string;
  reasoning: string;
  alternatives: string;
}

export interface AnalysisReport {
  analysis_summary: string;
  products: AnalyzedProduct[];
  unknown_unknowns: UnknownUnknownAnalysis[];
  final_recommendation: FinalRecommendation;
}

export interface RefinementResponse {
  refinement: string;
  conversation_history: Anthropic.MessageParam[];
}

export class AnalyzerAgent {
  private client: Anthropic;
  private model = "claude-sonnet-4-20250514";
  private conversationHistory: Anthropic.MessageParam[] = [];

  constructor(apiKey: string) {
    this.client = new Anthropic({ apiKey });
  }

  private buildSystemPrompt(): string {
    return `You are an expert product analyzer specializing in electronics. Your role is to:

1. Analyze product data against user requirements
2. Identify how well each product matches user needs
3. Uncover "unknown unknowns" - important factors the user may not have considered
4. Create clear, actionable ratings and comparisons
5. Provide a confident recommendation based on objective analysis

CRITICAL OUTPUT FORMAT:
You must structure your response in the following JSON format:

{
  "analysis_summary": "Brief overview of the analysis approach and key findings",
  "products": [
    {
      "rank": 1,
      "name": "Product Name",
      "price": "$XXX",
      "overall_rating": 9.2,
      "match_score": 95,
      "pros": ["List of strengths"],
      "cons": ["List of weaknesses"],
      "key_specs": {"spec_name": "value"},
      "ratings": {
        "value_for_money": 9.0,
        "performance": 9.5,
        "build_quality": 8.5,
        "user_reviews": 9.0
      },
      "why_this_product": "Explanation of why this ranks where it does",
      "best_for": "Type of user this is ideal for"
    }
  ],
  "unknown_unknowns": [
    {
      "factor": "Factor name",
      "why_it_matters": "Explanation",
      "impact": "How this affects the decision"
    }
  ],
  "final_recommendation": {
    "top_pick": "Product name",
    "reasoning": "Clear explanation of why this is the best choice",
    "alternatives": "When to consider other options"
  }
}

Be objective, data-driven, and consumer-focused. Avoid marketing language.`;
  }

  private buildAnalysisPrompt(
    userRequirements: UserRequirements,
    researchData: ResearchResults,
    maxProducts: number
  ): string {
    const requirementsStr = JSON.stringify(userRequirements, null, 2);
    const researchStr = JSON.stringify(researchData, null, 2);

    return `Please analyze the following product data and generate a comprehensive report.

USER REQUIREMENTS:
${requirementsStr}

RESEARCH DATA:
${researchStr}

INSTRUCTIONS:
1. Select the TOP ${maxProducts} products that best match the user's requirements
2. Include multiple products from the same brand if they have different features, models, or price points
3. Do NOT limit yourself to one product per brand - diversity in options is more important than brand variety
4. Rate each product on multiple dimensions (0-10 scale)
5. Calculate an overall match score (0-100%) based on how well it meets user needs
6. Identify "unknown unknowns" - important factors the user should consider but didn't mention
7. Provide a clear final recommendation with reasoning

Focus on making this report extremely easy to scan and understand. Prioritize clarity and actionability.

Output your analysis in the exact JSON format specified in your system instructions.`;
  }

  async analyzeProducts(
    userRequirements: UserRequirements,
    researchData: ResearchResults,
    maxProducts: number = 10
  ): Promise<AnalysisReport> {
    console.log("🤔 Starting product analysis...");

    const systemPrompt = this.buildSystemPrompt();
    const userPrompt = this.buildAnalysisPrompt(
      userRequirements,
      researchData,
      maxProducts
    );

    // Reset conversation for new analysis
    this.conversationHistory = [];

    // Call Claude to perform analysis
    const response = await this.client.messages.create({
      model: this.model,
      max_tokens: 4000,
      system: systemPrompt,
      messages: [
        {
          role: "user",
          content: userPrompt,
        },
      ],
    });

    const textContent = response.content.find((block) => block.type === "text");
    if (!textContent || textContent.type !== "text") {
      throw new Error("No text content in response");
    }

    const analysisText = textContent.text;

    // Store in conversation history
    this.conversationHistory.push({
      role: "user",
      content: userPrompt,
    });
    this.conversationHistory.push({
      role: "assistant",
      content: analysisText,
    });

    // Parse structured output
    const analysisResult = this.parseAnalysisResponse(analysisText);

    console.log(`✅ Analysis complete! Analyzed ${analysisResult.products.length} products`);

    return analysisResult;
  }

  private parseAnalysisResponse(responseText: string): AnalysisReport {
    try {
      // Try to extract JSON from the response
      const startIdx = responseText.indexOf("{");
      const endIdx = responseText.lastIndexOf("}") + 1;

      if (startIdx !== -1 && endIdx > startIdx) {
        const jsonStr = responseText.substring(startIdx, endIdx);
        return JSON.parse(jsonStr) as AnalysisReport;
      } else {
        throw new Error("Could not extract JSON format");
      }
    } catch (error) {
      console.error("JSON parsing error:", error);
      // Return a minimal valid structure
      return {
        analysis_summary: "Error parsing analysis",
        products: [],
        unknown_unknowns: [],
        final_recommendation: {
          top_pick: "N/A",
          reasoning: "Analysis parsing failed",
          alternatives: "Please try again",
        },
      };
    }
  }

  formatReportForDisplay(analysisResult: AnalysisReport): string {
    const report: string[] = [];

    report.push("=".repeat(80));
    report.push("PRODUCT ANALYSIS REPORT");
    report.push("=".repeat(80));
    report.push("");

    // Analysis Summary
    if (analysisResult.analysis_summary) {
      report.push("OVERVIEW");
      report.push("-".repeat(80));
      report.push(analysisResult.analysis_summary);
      report.push("");
    }

    // Products
    if (analysisResult.products && analysisResult.products.length > 0) {
      report.push("TOP RECOMMENDATIONS");
      report.push("-".repeat(80));
      report.push("");

      for (const product of analysisResult.products) {
        const rank = product.rank || "?";
        const name = product.name || "Unknown Product";
        const price = product.price || "N/A";
        const overallRating = product.overall_rating || 0;
        const matchScore = product.match_score || 0;

        report.push(`#${rank} - ${name}`);
        report.push(
          `Price: ${price} | Overall Rating: ${overallRating}/10 | Match: ${matchScore}%`
        );
        report.push("");

        // Ratings breakdown
        if (product.ratings) {
          report.push("Ratings:");
          for (const [criterion, score] of Object.entries(product.ratings)) {
            const filledBars = Math.floor(score);
            const emptyBars = 10 - filledBars;
            const bar = "█".repeat(filledBars) + "░".repeat(emptyBars);
            const formattedCriterion = criterion
              .replace(/_/g, " ")
              .replace(/\b\w/g, (l) => l.toUpperCase());
            report.push(`  ${formattedCriterion}: ${bar} ${score}/10`);
          }
          report.push("");
        }

        // Pros and Cons
        if (product.pros && product.pros.length > 0) {
          report.push("✓ PROS:");
          for (const pro of product.pros) {
            report.push(`  • ${pro}`);
          }
          report.push("");
        }

        if (product.cons && product.cons.length > 0) {
          report.push("✗ CONS:");
          for (const con of product.cons) {
            report.push(`  • ${con}`);
          }
          report.push("");
        }

        // Key Specs
        if (product.key_specs && Object.keys(product.key_specs).length > 0) {
          report.push("Key Specifications:");
          for (const [spec, value] of Object.entries(product.key_specs)) {
            report.push(`  ${spec}: ${value}`);
          }
          report.push("");
        }

        // Why this product
        if (product.why_this_product) {
          report.push(`Why #${rank}: ${product.why_this_product}`);
          report.push("");
        }

        if (product.best_for) {
          report.push(`Best For: ${product.best_for}`);
          report.push("");
        }

        report.push("-".repeat(80));
        report.push("");
      }
    }

    // Unknown Unknowns
    if (analysisResult.unknown_unknowns && analysisResult.unknown_unknowns.length > 0) {
      report.push("⚠ THINGS TO CONSIDER (Unknown Unknowns)");
      report.push("-".repeat(80));
      for (const unknown of analysisResult.unknown_unknowns) {
        report.push(`• ${unknown.factor}`);
        report.push(`  Why it matters: ${unknown.why_it_matters}`);
        report.push(`  Impact: ${unknown.impact}`);
        report.push("");
      }
    }

    // Final Recommendation
    if (analysisResult.final_recommendation) {
      const rec = analysisResult.final_recommendation;
      report.push("🏆 FINAL RECOMMENDATION");
      report.push("=".repeat(80));
      report.push(`Top Pick: ${rec.top_pick || "N/A"}`);
      report.push("");
      report.push(`Reasoning: ${rec.reasoning || ""}`);
      report.push("");
      if (rec.alternatives) {
        report.push(`Alternatives: ${rec.alternatives}`);
      }
      report.push("");
    }

    report.push("=".repeat(80));

    return report.join("\n");
  }

  async refineAnalysis(userFeedback: string): Promise<RefinementResponse> {
    this.conversationHistory.push({
      role: "user",
      content: userFeedback,
    });

    const response = await this.client.messages.create({
      model: this.model,
      max_tokens: 2000,
      messages: this.conversationHistory,
    });

    const textContent = response.content.find((block) => block.type === "text");
    if (!textContent || textContent.type !== "text") {
      throw new Error("No text content in response");
    }

    const refinement = textContent.text;

    this.conversationHistory.push({
      role: "assistant",
      content: refinement,
    });

    return {
      refinement,
      conversation_history: [...this.conversationHistory],
    };
  }
}
