import { NextRequest, NextResponse } from 'next/server';
import { PlannerAgent } from '@/lib/agents/PlannerAgent';
import { ResearchAgent } from '@/lib/agents/ResearchAgent';
import { AnalyzerAgent } from '@/lib/agents/AnalyzerAgent';
import { RecommendationAgent } from '@/lib/agents/RecommendationAgent';
import type { UserRequirements } from '@/lib/types';

// Store agent instances and session data per session
interface SessionData {
  plannerAgent: PlannerAgent;
  requirements?: UserRequirements;
  researchResults?: any;
  searchQueries?: string[];
}

const agentSessions = new Map<string, SessionData>();

function getOrCreateSession(sessionId: string): SessionData {
  if (!agentSessions.has(sessionId)) {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      throw new Error('ANTHROPIC_API_KEY not configured');
    }
    agentSessions.set(sessionId, {
      plannerAgent: new PlannerAgent(apiKey),
    });
  }
  return agentSessions.get(sessionId)!;
}

export async function POST(request: NextRequest) {
  try {
    const { message, phase, sessionId = 'default' } = await request.json();

    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📥 API Route received request');
    console.log('  Session:', sessionId);
    console.log('  Phase:', phase);
    console.log('  User message:', message);
    console.log('  Auto-continue:', message === '[AUTO_CONTINUE]');

    const session = getOrCreateSession(sessionId);
    let response = '';
    let newPhase = phase;

    if (phase === 'planning') {
      // Use REAL PlannerAgent
      console.log('🤖 Calling PlannerAgent (Claude)...');
      const result = await session.plannerAgent.chat(message);

      response = result.conversation;

      console.log('  Assessment:', {
        status: result.assessment.status,
        confidence: result.assessment.confidence_score,
        questionCount: result.assessment.question_count,
      });

      // Check if planning is complete
      if (result.isComplete) {
        console.log('✅ Planning complete! Moving to research phase');
        newPhase = 'researching';

        // Store requirements for next phase
        session.requirements = session.plannerAgent.getFinalRequirements();
        console.log('  Final requirements:', session.requirements);

        // Generate search queries immediately so UI can show them
        const apiKey = process.env.ANTHROPIC_API_KEY!;
        const researchAgent = new ResearchAgent(apiKey);
        try {
          const queries = await researchAgent.generateSearchQueries(session.requirements);
          session.searchQueries = queries;
          console.log('  Generated search queries:', queries);
        } catch (error) {
          console.error('  Failed to generate queries:', error);
          session.searchQueries = [];
        }

        // Add a personal touch to the transition message
        response += "\n\nPerfect! Let me search for the best options. I'll check with my favorite retailers and find you some great deals.";
      }
    } else if (phase === 'researching' && message === '[AUTO_CONTINUE]') {
      // Use REAL ResearchAgent
      if (!session.requirements) {
        throw new Error('No requirements available for research');
      }

      console.log('🔍 Calling ResearchAgent...');
      const apiKey = process.env.ANTHROPIC_API_KEY!;
      const parallelKey = process.env.PARALLEL_API_KEY;

      if (!parallelKey) {
        throw new Error('PARALLEL_API_KEY not configured');
      }

      const researchAgent = new ResearchAgent(apiKey);
      const researchResult = await researchAgent.research(session.requirements);

      console.log('  Research result:', {
        productsFound: researchResult.products_found?.length || 0,
        unknownUnknowns: researchResult.unknown_unknowns?.length || 0,
        queriesUsed: researchResult.search_queries_used?.length || 0,
      });

      // Create response from research results
      const productCount = researchResult.products_found?.length || 0;
      const unknownCount = researchResult.unknown_unknowns?.length || 0;

      response = `Great news! I found ${productCount} excellent options for you across Amazon, Best Buy, Walmart, and other retailers. ${unknownCount > 0 ? `I also discovered ${unknownCount} important ${unknownCount === 1 ? 'factor' : 'factors'} you might want to consider.` : ''}\n\nLet me take a closer look at these and put together my recommendations...`;
      session.researchResults = researchResult;
      // Update search queries from actual research if they weren't set earlier
      if (!session.searchQueries || session.searchQueries.length === 0) {
        session.searchQueries = researchResult.search_queries_used || [];
      }

      newPhase = 'analyzing';
    } else if (phase === 'analyzing' && message === '[AUTO_CONTINUE]') {
      // Use AnalyzerAgent + RecommendationAgent
      if (!session.requirements || !session.researchResults) {
        throw new Error('No research results available for analysis');
      }

      console.log('📊 Calling AnalyzerAgent...');
      const apiKey = process.env.ANTHROPIC_API_KEY!;
      const analyzerAgent = new AnalyzerAgent(apiKey);

      const analysisResult = await analyzerAgent.analyzeProducts(
        session.requirements,
        session.researchResults
      );

      console.log('  Analysis complete:', {
        productsAnalyzed: analysisResult.products?.length || 0,
        unknownUnknownsFound: analysisResult.unknown_unknowns?.length || 0,
      });

      // Now generate conversational recommendation
      console.log('💬 Calling RecommendationAgent...');
      const recommendationAgent = new RecommendationAgent(apiKey);

      const recommendation = await recommendationAgent.generateRecommendation(
        session.requirements,
        analysisResult
      );

      // Join multiple messages with double line breaks for visual separation
      response = recommendation.messages.join('\n\n');

      console.log(`  Generated ${recommendation.messages.length} recommendation messages`);

      newPhase = 'complete';
    }

    // Ensure response is never empty
    if (!response) {
      console.error('⚠️  WARNING: Empty response generated!');
      response = "I'm working on your request...";
    }

    console.log('📤 API sending response:');
    console.log('  Response:', response.substring(0, 100) + (response.length > 100 ? '...' : ''));
    console.log('  New phase:', newPhase);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

    return NextResponse.json({
      response,
      phase: newPhase,
      searchQueries: session.searchQueries || [],
    });
  } catch (error) {
    console.error('❌ API error:', error);
    return NextResponse.json(
      { error: 'Something went wrong' },
      { status: 500 }
    );
  }
}
