/**
 * Research Agent - Web Search & Product Analysis
 * - Searches web for products matching user requirements
 * - Processes and analyzes information
 * - Identifies unknown unknowns (things user should consider but didn't mention)
 */

import Anthropic from "@anthropic-ai/sdk";
import { UserRequirements } from "./PlannerAgent";

export interface ProductInfo {
  name: string;
  price: number | null;
  url: string;
  key_specs: Record<string, any>;
  pros: string[];
  cons: string[];
  source: string;
}

export interface UnknownUnknown {
  factor: string;
  why_matters: string;
  what_to_look_for: string;
}

export interface MarketInsights {
  typical_price_range?: string;
  key_differentiators?: string[];
  current_trends?: string[];
  red_flags?: string[];
}

export interface ResearchResults {
  products_found: ProductInfo[];
  unknown_unknowns: UnknownUnknown[];
  market_insights: MarketInsights;
  search_queries_used: string[];
}

interface SearchResult {
  query: string;
  content: string;
}

interface AnalysisResult {
  products: ProductInfo[];
  unknown_unknowns: UnknownUnknown[];
  market_insights: MarketInsights;
}

export class ResearchAgent {
  private client: Anthropic;
  private model = "claude-sonnet-4-20250514";
  private searchQueries: string[] = [];

  constructor(apiKey: string) {
    this.client = new Anthropic({ apiKey });
  }

  private createSearchStrategyPrompt(requirements: UserRequirements): string {
    const today = new Date();
    const currentYear = today.getFullYear();
    const currentMonth = today.toLocaleString('default', { month: 'long' });
    const todayDate = `${currentMonth} ${currentYear}`;

    return `Given these user requirements for electronics shopping:
${JSON.stringify(requirements, null, 2)}

TODAY'S DATE: ${todayDate}

Create a search strategy focusing on CURRENT, UP-TO-DATE information. Generate 3-5 web search queries.

CRITICAL REQUIREMENTS:
- Focus on LATEST products available NOW (${currentYear})
- Target popular e-commerce sites: Amazon, Best Buy, Walmart, Target, Newegg
- Include queries for current pricing (sales, discounts happening NOW)
- Include queries for recent user reviews

Query format examples:
- "best [product] ${currentYear} Amazon"
- "[product] current price Best Buy ${currentMonth} ${currentYear}"
- "[product] user reviews ${currentYear}"
- "[product] deals discounts ${currentMonth} ${currentYear}"

Return ONLY a JSON array of search queries:
["query 1", "query 2", "query 3"]`;
  }

  private createAnalysisPrompt(
    requirements: UserRequirements,
    searchResults: SearchResult[]
  ): string {
    const today = new Date();
    const currentYear = today.getFullYear();
    const currentMonth = today.toLocaleString('default', { month: 'long' });

    return `You are analyzing CURRENT web search results to help a user find electronics products.

TODAY'S DATE: ${currentMonth} ${currentYear}

USER REQUIREMENTS:
${JSON.stringify(requirements, null, 2)}

SEARCH RESULTS (from e-commerce sites):
${JSON.stringify(searchResults, null, 2)}

Your task:
1. LIST ALL PRODUCTS mentioned in the search results that match the user's requirements
2. Use the LATEST PRICING from search results (including any sales/discounts happening now)
3. Include RECENT USER REVIEWS and ratings from the search results
4. Identify "unknown unknowns" - important factors the user didn't mention but should consider
5. Provide market insights based on CURRENT trends (${currentYear})

CRITICAL - MULTIPLE PRODUCTS PER BRAND:
This is NOT a "best of each brand" roundup. This is a COMPREHENSIVE CATALOG.

If the search results mention multiple models/variants from the same brand - LIST ALL OF THEM.
Do NOT pick just one "representative" product per brand. Include EVERY model that fits the requirements.

Think of this like creating a product catalog, not curating a "best of" list.

REQUIRED BEHAVIOR:
✅ DO: Include all models from the same brand if they match requirements (even if 5+ products)
✅ DO: List products at different price points within the same brand
✅ DO: Include both newer and older generation products if both are available and relevant
❌ DON'T: Pick one "representative" product per brand
❌ DON'T: Limit yourself to brand diversity over model diversity
❌ DON'T: Filter down to fewer products for the sake of variety

TARGET: 10-15 total products. More is better than less.

OTHER REQUIREMENTS:
- Prioritize products that are currently in stock and available
- Use actual prices from Amazon, Best Buy, Walmart, etc. found in search results
- Include user review sentiment and ratings from e-commerce sites
- Note any ongoing sales or promotions

UNKNOWN UNKNOWNS examples:
- For laptops: battery life, weight, upgrade ability, thermal management
- For headphones: comfort for long sessions, ANC quality, call quality
- For phones: update support duration, repairability, ecosystem lock-in

Return ONLY valid JSON in this format:
{
    "products": [
        {
            "name": "Product Name",
            "price": 999.99,
            "url": "https://...",
            "key_specs": {"spec": "value"},
            "pros": ["pro 1", "pro 2"],
            "cons": ["con 1", "con 2"],
            "source": "source domain"
        }
    ],
    "unknown_unknowns": [
        {
            "factor": "Battery Life",
            "why_matters": "Gaming laptops often have poor battery life, affecting portability",
            "what_to_look_for": "Look for 6+ hours of real-world usage"
        }
    ],
    "market_insights": {
        "typical_price_range": "800-1500",
        "key_differentiators": ["GPU performance", "cooling system"],
        "current_trends": ["RTX 40 series becoming standard", "DDR5 now common"],
        "red_flags": ["Single channel RAM", "Poor thermals"]
    }
}`;
  }

  async research(requirements: UserRequirements): Promise<ResearchResults> {
    console.log("🔍 Starting research phase...");

    // Step 1: Generate search queries
    console.log("\n📋 Planning search strategy...");
    const searchQueries = await this.generateSearchQueries(requirements);
    this.searchQueries = searchQueries;
    console.log(`   Generated ${searchQueries.length} search queries`);

    // Step 2: Execute web searches
    console.log("\n🌐 Searching the web...");
    const allSearchResults: SearchResult[] = [];
    for (let i = 0; i < searchQueries.length; i++) {
      const query = searchQueries[i];
      console.log(`   [${i + 1}/${searchQueries.length}] Searching: ${query}`);
      const results = await this.webSearch(query);
      allSearchResults.push(...results);
    }

    console.log(`   Found ${allSearchResults.length} total results`);

    // Step 3: Analyze and extract product info
    console.log("\n🤔 Analyzing results...");
    const analysis = await this.analyzeResults(requirements, allSearchResults);

    // Step 4: Convert to ResearchResults
    const results: ResearchResults = {
      products_found: analysis.products,
      unknown_unknowns: analysis.unknown_unknowns,
      market_insights: analysis.market_insights,
      search_queries_used: searchQueries,
    };

    console.log(`\n✅ Research complete! Found ${results.products_found.length} products`);
    console.log(`   Identified ${results.unknown_unknowns.length} unknown unknowns`);

    // Save raw search results for debugging
    if (process.env.DEBUG === "true") {
      const fs = await import("fs");
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      const debugFile = `debug-research-${timestamp}.json`;
      fs.writeFileSync(
        debugFile,
        JSON.stringify(
          {
            requirements,
            searchQueries,
            rawSearchResults: allSearchResults,
            analysis,
            finalResults: results,
          },
          null,
          2
        )
      );
      console.log(`   🐛 Debug data saved to: ${debugFile}`);
    }

    return results;
  }

  async generateSearchQueries(
    requirements: UserRequirements
  ): Promise<string[]> {
    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: 1000,
        messages: [
          {
            role: "user",
            content: this.createSearchStrategyPrompt(requirements),
          },
        ],
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

      const queries = JSON.parse(jsonText) as string[];
      return queries;
    } catch (error) {
      console.error("Error generating queries:", error);

      // Fallback queries with current year
      const currentYear = new Date().getFullYear();
      const productType = requirements.product_type || "electronics";
      const budget = requirements.budget_max;
      return [
        `best ${productType} ${currentYear} Amazon`,
        budget ? `${productType} under $${budget} Best Buy ${currentYear}` : `${productType} reviews ${currentYear}`,
        `${productType} comparison ${currentYear}`,
      ];
    }
  }

  private async webSearch(query: string): Promise<SearchResult[]> {
    try {
      const parallelApiKey = process.env.PARALLEL_API_KEY;

      if (!parallelApiKey) {
        throw new Error("PARALLEL_API_KEY not found in environment variables");
      }

      const today = new Date();
      const currentYear = today.getFullYear();
      const currentMonth = today.toLocaleString('default', { month: 'long' });

      // Use Parallel AI's search API for actual web search with recency focus
      const axios = (await import("axios")).default;

      const enhancedObjective = `${query}

SEARCH FOCUS:
- Prioritize results from: Amazon.com, BestBuy.com, Walmart.com, Target.com, Newegg.com
- Look for CURRENT pricing (${currentMonth} ${currentYear})
- Find active sales, discounts, promotions happening NOW
- Include recent user reviews and ratings (${currentYear})
- Focus on products currently in stock and available for purchase

Get the most recent and accurate information possible.`;

      const response = await axios.post(
        "https://api.parallel.ai/v1beta/search",
        {
          mode: "one-shot",
          search_queries: null,
          max_results: 15, // Increased for better coverage
          objective: enhancedObjective,
        },
        {
          headers: {
            "Content-Type": "application/json",
            "x-api-key": parallelApiKey,
            "parallel-beta": "search-extract-2025-10-10",
          },
          timeout: 30000, // 30 second timeout
        }
      );

      // Extract search results from Parallel AI response
      const searchResults: SearchResult[] = [];

      if (response.data) {
        // Debug: Log what we got from Parallel AI
        console.log(`   ✓ Received response with ${JSON.stringify(response.data).length} characters`);

        searchResults.push({
          query,
          content: JSON.stringify(response.data, null, 2),
        });
      } else {
        console.log(`   ⚠ No data received from Parallel AI for query: ${query}`);
      }

      return searchResults;
    } catch (error) {
      console.error(`Search error for '${query}':`, error);
      return [];
    }
  }

  private async analyzeResults(
    requirements: UserRequirements,
    searchResults: SearchResult[]
  ): Promise<AnalysisResult> {
    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: 4096,
        messages: [
          {
            role: "user",
            content: this.createAnalysisPrompt(requirements, searchResults),
          },
        ],
      });

      const textContent = response.content.find((block) => block.type === "text");
      if (!textContent || textContent.type !== "text") {
        throw new Error("No text content in response");
      }

      let text = textContent.text.trim();

      // Try to extract JSON from code blocks
      if (text.includes("```json")) {
        text = text.split("```json")[1].split("```")[0].trim();
      } else if (text.includes("```")) {
        text = text.split("```")[1].split("```")[0].trim();
      }

      const analysis = JSON.parse(text) as AnalysisResult;
      return analysis;
    } catch (error) {
      console.error("Analysis error:", error);
      return {
        products: [],
        unknown_unknowns: [],
        market_insights: {},
      };
    }
  }

  formatResultsForUser(
    results: ResearchResults,
    requirements: UserRequirements
  ): string {
    const output: string[] = [];

    output.push("=".repeat(60));
    output.push("RESEARCH RESULTS");
    output.push("=".repeat(60));

    // Products found
    output.push(`\n📦 Found ${results.products_found.length} Products:\n`);
    results.products_found.forEach((product, i) => {
      output.push(`${i + 1}. ${product.name}`);
      if (product.price) {
        output.push(`   💰 Price: $${product.price}`);
      }
      output.push(`   🔗 ${product.url}`);
      if (Object.keys(product.key_specs).length > 0) {
        output.push(`   📊 Specs: ${JSON.stringify(product.key_specs)}`);
      }
      if (product.pros.length > 0) {
        output.push(`   ✅ Pros: ${product.pros.join(", ")}`);
      }
      if (product.cons.length > 0) {
        output.push(`   ❌ Cons: ${product.cons.join(", ")}`);
      }
      output.push("");
    });

    // Unknown unknowns
    if (results.unknown_unknowns.length > 0) {
      output.push("\n💡 Things You Should Also Consider:\n");
      results.unknown_unknowns.forEach((uu) => {
        output.push(`• ${uu.factor}`);
        output.push(`  Why: ${uu.why_matters}`);
        output.push(`  Look for: ${uu.what_to_look_for}`);
        output.push("");
      });
    }

    // Market insights
    if (Object.keys(results.market_insights).length > 0) {
      output.push("\n📊 Market Insights:\n");
      const insights = results.market_insights;
      if (insights.typical_price_range) {
        output.push(`💵 Typical Price Range: $${insights.typical_price_range}`);
      }
      if (insights.key_differentiators) {
        output.push(`🎯 Key Differentiators: ${insights.key_differentiators.join(", ")}`);
      }
      if (insights.current_trends) {
        output.push(`📈 Current Trends: ${insights.current_trends.join(", ")}`);
      }
      if (insights.red_flags) {
        output.push(`🚩 Red Flags to Avoid: ${insights.red_flags.join(", ")}`);
      }
    }

    output.push("\n" + "=".repeat(60));

    return output.join("\n");
  }
}
