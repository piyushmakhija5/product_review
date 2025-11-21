/**
 * Core type definitions for the Product Review Agent system
 */

export type AgentRole = "planner" | "researcher" | "analyzer" | "coordinator";

export type WorkflowStage =
  | "initializing"
  | "planning"
  | "collecting"
  | "researching"
  | "analyzing"
  | "reporting"
  | "complete"
  | "error";

export type DecisionStatus = "ready" | "need_more_info" | "insufficient_info" | "error";

/**
 * User requirements for product search
 */
export interface UserRequirements {
  // Core requirements
  productCategory: string;
  budgetMin?: number;
  budgetMax?: number;

  // Specifications
  mustHaveSpecs: Record<string, any>;
  niceToHaveSpecs: Record<string, any>;

  // Context
  useCase: string;
  priorities: string[]; // What matters most: price, quality, brand, etc.
  dealBreakers: string[]; // Absolute no-gos

  // Metadata
  completenessScore: number; // 0-1
  confidence: number; // 0-1
  rawInput: string;
  conversationHistory: string[];
}

/**
 * Planning decision from the Planner agent
 */
export interface PlanningDecision {
  status: DecisionStatus;
  confidence: number;
  missingFields: string[];
  suggestedQuestions: string[];
  requirements?: UserRequirements;
  reasoning: string;
}

/**
 * Product information
 */
export interface Product {
  id: string;
  name: string;
  brand: string;
  price: number;
  currency: string;

  // Availability
  inStock: boolean;
  retailer: string;
  url: string;

  // Ratings
  rating: number;
  reviewCount: number;

  // Specifications
  specifications: Record<string, any>;

  // Additional data
  description?: string;
  imageUrl?: string;
  pros?: string[];
  cons?: string[];

  // Analysis
  matchScore?: number; // 0-100
  valueScore?: number; // 0-100

  // Metadata
  scrapedAt: Date;
  source: string;
}

/**
 * Research results from the Research agent
 */
export interface ResearchResults {
  products: Product[];
  totalFound: number;
  searchQueries: string[];
  retailers: string[];
  searchDuration: number;
  metadata: {
    timestamp: Date;
    requirements: UserRequirements;
    errors?: string[];
  };
}

/**
 * Analysis results and report
 */
export interface AnalysisReport {
  // Top recommendations
  topProducts: Product[];

  // Analysis
  summary: string;
  marketInsights: string;
  recommendations: Recommendation[];

  // Comparison
  comparisonMatrix: ComparisonMatrix;

  // Warnings and notes
  unknownUnknowns: string[];
  warnings: string[];

  // Metadata
  generatedAt: Date;
  confidence: number;
}

/**
 * Individual product recommendation
 */
export interface Recommendation {
  product: Product;
  rank: number;
  overallScore: number;
  reasoning: string;
  bestFor: string; // e.g., "Best value", "Best performance", "Best for gaming"
  pros: string[];
  cons: string[];
  verdict: string;
}

/**
 * Comparison matrix for products
 */
export interface ComparisonMatrix {
  headers: string[]; // Feature names
  rows: ComparisonRow[];
}

export interface ComparisonRow {
  product: Product;
  values: (string | number | boolean)[];
  highlights: boolean[]; // Which values are highlighted as good
}

/**
 * Agent configuration
 */
export interface AgentConfig {
  name: string;
  role: AgentRole;
  model: string;
  maxTokens: number;
  temperature: number;
  systemPrompt: string;
}

/**
 * Agent handoff request
 */
export interface HandoffRequest {
  fromAgent: string;
  toAgent: string;
  context: Record<string, any>;
  data: any;
  timestamp: Date;
}

/**
 * Agent response
 */
export interface AgentResponse<T = any> {
  agent: string;
  success: boolean;
  data: T;
  error?: string;
  handoffTo?: string;
  handoffData?: any;
  metadata: {
    duration: number;
    tokensUsed?: number;
    timestamp: Date;
  };
}

/**
 * Workflow state
 */
export interface WorkflowState {
  stage: WorkflowStage;
  currentAgent?: string;

  // Data
  requirements?: UserRequirements;
  researchResults?: ResearchResults;
  analysisReport?: AnalysisReport;

  // History
  conversationHistory: ConversationMessage[];
  agentHandoffs: HandoffRequest[];

  // Metadata
  startTime: Date;
  errors: string[];
  retryCount: number;
}

/**
 * Conversation message
 */
export interface ConversationMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

/**
 * Search tool parameters
 */
export interface SearchParams {
  query: string;
  retailers?: string[];
  maxResults?: number;
  priceRange?: {
    min: number;
    max: number;
  };
  filters?: Record<string, any>;
}

/**
 * Tool execution result
 */
export interface ToolResult {
  toolName: string;
  success: boolean;
  data: any;
  error?: string;
  duration: number;
}
