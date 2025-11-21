/**
 * Recommendation Agent - Conversational Product Recommendations
 * - Takes structured analysis data
 * - Generates warm, conversational recommendations
 * - Presents findings in a user-friendly, concierge style
 */

import Anthropic from "@anthropic-ai/sdk";
import { AnalysisReport } from "./AnalyzerAgent";
import { UserRequirements } from "./PlannerAgent";

export interface ConversationalRecommendation {
  messages: string[];
  structured_data: AnalysisReport;
}

export class RecommendationAgent {
  private client: Anthropic;
  private model = "claude-sonnet-4-20250514";

  constructor(apiKey: string) {
    this.client = new Anthropic({ apiKey });
  }

  private buildRecommendationPrompt(
    requirements: UserRequirements,
    analysis: AnalysisReport
  ): string {
    const requirementsStr = JSON.stringify(requirements, null, 2);
    const analysisStr = JSON.stringify(analysis, null, 2);

    return `You are Claudia, a personal shopping concierge. You've just finished analyzing products for a customer.

USER'S REQUIREMENTS:
${requirementsStr}

YOUR ANALYSIS:
${analysisStr}

YOUR TASK:
Write 2-3 SUPER SHORT messages, like quick texts. Each message should be 1-2 sentences MAX.

MESSAGE 1: Top Pick (1-2 sentences)
- Your #1 recommendation with price
- ONE clear reason why

MESSAGE 2: Alternative (1 sentence, OPTIONAL)
- ONE alternative if it's significantly different (cheaper, different tradeoff)
- Skip if not needed

MESSAGE 3: Watch Out (1 sentence, OPTIONAL)
- ONE critical thing they should know
- Skip if nothing crucial

CRITICAL RULES:
- Maximum 1-2 sentences per message
- Be PUNCHY and DIRECT
- No explanations, just the key point
- Sound like texting, not talking

FORMAT YOUR RESPONSE:
Separate each message with exactly "---MESSAGE---" on its own line.

Example:
My top pick is the [Product] at $X - it has [key feature] that's perfect for [their need].

---MESSAGE---

If budget matters, the [Alternative] at $Y gets you 80% of the performance for half the price.

---MESSAGE---

Watch out - [critical consideration].`;
  }

  async generateRecommendation(
    requirements: UserRequirements,
    analysis: AnalysisReport
  ): Promise<ConversationalRecommendation> {
    console.log("💬 Generating conversational recommendation...");

    const response = await this.client.messages.create({
      model: this.model,
      max_tokens: 2000,
      messages: [
        {
          role: "user",
          content: this.buildRecommendationPrompt(requirements, analysis),
        },
      ],
    });

    const textContent = response.content.find((block) => block.type === "text");
    if (!textContent || textContent.type !== "text") {
      throw new Error("No text content in response");
    }

    const fullText = textContent.text.trim();

    // Split by delimiter and clean up messages
    const messages = fullText
      .split("---MESSAGE---")
      .map(msg => msg.trim())
      .filter(msg => msg.length > 0);

    console.log(`✅ Generated ${messages.length} conversational messages`);

    return {
      messages,
      structured_data: analysis,
    };
  }
}
