/**
 * Planner Agent - Collects user requirements systematically
 * - One question at a time
 * - Short, casual responses (GenZ/Millennial tone)
 * - Smart stopping after 3-4 questions
 * - NO product recommendations
 */

import Anthropic from "@anthropic-ai/sdk";

export type InformationStatus = "insufficient" | "sufficient" | "needs_clarification" | "ready_for_confirmation";

export interface UserRequirements {
  product_type: string | null;
  budget_min: number | null;
  budget_max: number | null;
  color: string | null;
  specifications: Record<string, any>;
  brand_preferences: string[];
  use_case: string | null;
  additional_constraints: Record<string, any>;
}

export interface PlanningAssessment {
  status: InformationStatus;
  missing_critical: string[];
  question_count: number;
  confidence_score: number;
  reasoning: string;
  next_question_priority: string;
}

export interface ChatResponse {
  conversation: string;
  assessment: PlanningAssessment;
  isComplete: boolean;
}

export class PlannerAgent {
  private client: Anthropic;
  private model = "claude-sonnet-4-20250514";
  private conversationHistory: Anthropic.MessageParam[] = [];
  private requirements: UserRequirements;
  private questionCount = 0;

  constructor(apiKey: string) {
    this.client = new Anthropic({ apiKey });
    this.requirements = this.createEmptyRequirements();
  }

  private createEmptyRequirements(): UserRequirements {
    return {
      product_type: null,
      budget_min: null,
      budget_max: null,
      color: null,
      specifications: {},
      brand_preferences: [],
      use_case: null,
      additional_constraints: {},
    };
  }

  private createSystemPrompt(): string {
    return `You're Claudia, a premium shopping concierge with Gen-Z energy. Keep it SHORT and casual.

YOUR ONLY JOB: Collect requirements from the user. DO NOT make product recommendations. DO NOT suggest specific products or brands unless the user asks about them.

RULES:
- Ask ONE question per response (never multiple)
- Keep responses to 1-2 sentences MAXIMUM (be extremely concise)
- Premium concierge vibe but casual Gen-Z language
- After 3-4 questions, you're done asking
- NEVER recommend specific products or models
- NEVER say things like "I'd recommend..." or "You should get..."
- NO verbose explanations - just ask what you need to know

CONVERSATIONAL STYLE (IMPORTANT):
- ALWAYS acknowledge what the user just said before asking your next question
- Show empathy and understanding (you're in service industry!)
- Make them feel heard and comfortable
- Examples:
  * User: "I'm too lazy to search online" → You: "I feel you! That's literally why I'm here. Budget?"
  * User: "I need a laptop" → You: "Perfect! What's your budget?"
  * User: "$500" → You: "Got it! What'll you mainly use it for?"
  * User: "Gaming and streaming" → You: "Nice! Any brands you prefer or avoid?"
- Quick acknowledgment + smooth transition to next question
- Warm but efficient - like a friend helping you shop

WHAT YOU NEED (priority order):
1. Product type (laptop, phone, etc.)
2. Budget (max price at least)
3. What they're using it for

FINAL CONFIRMATION STEP (IMPORTANT):
When you have enough information (type + budget + use case), BEFORE marking status as "sufficient":
- Say something like: "Cool, I think I have what I need! Any other must-haves I should know about?"
- Wait for user response
- ONLY mark status="sufficient" after this final confirmation

STOP ASKING WHEN:
- You have type + budget + use case
- You've asked the final confirmation question and user says to proceed
- You've asked 3-4 questions already
- They're getting annoyed

VIBE:
- Premium concierge but NOT verbose
- Acknowledge first, then ask
- "I feel you!" "Nice!" "Perfect!" "Love it!" "Say no more!"
- Ultra concise - every word counts
- Use contractions (you're, what's, that's)
- No corporate speak, no explanations, no fluff

At the end of each response, include this:
\`\`\`assessment
{
    "status": "insufficient|sufficient|needs_clarification|ready_for_confirmation",
    "missing_critical": ["list"],
    "question_count": number,
    "confidence_score": 0.0-1.0,
    "reasoning": "brief",
    "next_question_priority": "what next"
}
\`\`\`

Note: Use status="ready_for_confirmation" when you have basic info but haven't asked the final confirmation yet.`;
  }

  private extractAssessment(responseText: string): {
    conversation: string;
    assessment: PlanningAssessment;
  } {
    if (responseText.includes("```assessment")) {
      const parts = responseText.split("```assessment");
      const conversation = parts[0].trim();

      // Extract JSON from assessment block
      const assessmentBlock = parts[1].split("```")[0].trim();

      try {
        const assessment = JSON.parse(assessmentBlock) as PlanningAssessment;
        this.questionCount = assessment.question_count || this.questionCount;
        return { conversation, assessment };
      } catch (error) {
        console.error("Failed to parse assessment:", error);
        return {
          conversation,
          assessment: {
            status: "insufficient",
            missing_critical: ["unknown"],
            question_count: this.questionCount,
            confidence_score: 0.5,
            reasoning: "Failed to parse assessment",
            next_question_priority: "unknown",
          },
        };
      }
    }

    // No assessment block found
    return {
      conversation: responseText,
      assessment: {
        status: "insufficient",
        missing_critical: ["assessment_missing"],
        question_count: this.questionCount,
        confidence_score: 0.3,
        reasoning: "No structured assessment provided",
        next_question_priority: "unknown",
      },
    };
  }

  private async updateRequirements(
    userInput: string,
    assistantResponse: string
  ): Promise<void> {
    const extractionPrompt = `Based on this conversation exchange, extract any product requirements mentioned.

User said: ${userInput}
Assistant said: ${assistantResponse}

Current requirements: ${JSON.stringify(this.requirements, null, 2)}

Extract and return ONLY a JSON object with any NEW or UPDATED requirements. Use null for fields not mentioned.
Format:
{
    "product_type": "string or null",
    "budget_min": number or null,
    "budget_max": number or null,
    "color": "string or null",
    "specifications": {"key": "value"},
    "brand_preferences": ["list"],
    "use_case": "string or null",
    "additional_constraints": {"key": "value"}
}`;

    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: 1000,
        messages: [{ role: "user", content: extractionPrompt }],
      });

      const textContent = response.content.find((block) => block.type === "text");
      if (!textContent || textContent.type !== "text") {
        throw new Error("No text content in response");
      }

      // Strip code blocks if present
      let jsonText = textContent.text.trim();
      if (jsonText.includes("```json")) {
        jsonText = jsonText.split("```json")[1].split("```")[0].trim();
      } else if (jsonText.includes("```")) {
        jsonText = jsonText.split("```")[1].split("```")[0].trim();
      }

      const extracted = JSON.parse(jsonText) as Partial<UserRequirements>;

      // Update requirements
      for (const [key, value] of Object.entries(extracted)) {
        if (value !== null && value !== undefined) {
          if (key === "specifications" || key === "additional_constraints") {
            Object.assign(
              this.requirements[key as keyof UserRequirements] as Record<string, any>,
              value
            );
          } else if (key === "brand_preferences" && Array.isArray(value)) {
            const current = this.requirements.brand_preferences;
            this.requirements.brand_preferences = [
              ...current,
              ...value.filter((b: string) => !current.includes(b)),
            ];
          } else {
            (this.requirements as any)[key] = value;
          }
        }
      }
    } catch (error) {
      console.error("Requirements extraction error:", error);
    }
  }

  async chat(userInput: string): Promise<ChatResponse> {
    // Add user message to history
    this.conversationHistory.push({
      role: "user",
      content: userInput,
    });

    // Create context with current requirements and question count
    const context = `\nCurrent gathered requirements:\n${JSON.stringify(this.requirements, null, 2)}\nQuestions asked so far: ${this.questionCount}\n`;

    // Get response from Claude
    const response = await this.client.messages.create({
      model: this.model,
      max_tokens: 1500,
      system: this.createSystemPrompt(),
      messages: [
        ...this.conversationHistory,
        {
          role: "user",
          content: context,
        },
      ],
    });

    const textContent = response.content.find((block) => block.type === "text");
    if (!textContent || textContent.type !== "text") {
      throw new Error("No text content in response");
    }

    const assistantMessage = textContent.text;

    // Extract conversation and assessment
    const { conversation, assessment } = this.extractAssessment(assistantMessage);

    // Add only the conversation part to history
    this.conversationHistory.push({
      role: "assistant",
      content: conversation,
    });

    // Update requirements based on conversation
    await this.updateRequirements(userInput, conversation);

    // Determine if we're done (threshold: 0.7)
    const isComplete =
      assessment.status === "sufficient" && assessment.confidence_score >= 0.7;

    return {
      conversation,
      assessment,
      isComplete,
    };
  }

  getFinalRequirements(): UserRequirements {
    return { ...this.requirements };
  }

  getQuestionCount(): number {
    return this.questionCount;
  }

  getConversationHistory(): Anthropic.MessageParam[] {
    return [...this.conversationHistory];
  }

  restoreState(state: {
    conversationHistory: Anthropic.MessageParam[];
    requirements?: UserRequirements;
    questionCount?: number;
  }): void {
    this.conversationHistory = state.conversationHistory || [];
    if (state.requirements) {
      this.requirements = state.requirements;
    }
    if (state.questionCount !== undefined) {
      this.questionCount = state.questionCount;
    }
  }

  reset(): void {
    this.conversationHistory = [];
    this.requirements = this.createEmptyRequirements();
    this.questionCount = 0;
  }
}
