/**
 * Session Store - Handles session persistence with Redis
 * Falls back to in-memory storage if Redis unavailable
 */

import { getRedisClient } from '../redis';
import { PlannerAgent, UserRequirements } from '@/lib/agents/PlannerAgent';

export interface SessionData {
  sessionId: string;
  phase: 'planning' | 'researching' | 'analyzing' | 'complete';
  createdAt: number;
  lastActivityAt: number;

  // Serializable data
  requirements?: UserRequirements;
  searchQueries?: string[];
  researchResults?: any;

  // Agent state (serialized)
  plannerState?: {
    conversationHistory: any[];
    requirements?: UserRequirements;
    questionCount?: number;
  };
}

// In-memory fallback
const memoryStore = new Map<string, {
  data: SessionData;
  agent: PlannerAgent;
}>();

const SESSION_TTL = 3600; // 1 hour in seconds

export class SessionStore {
  private redis = getRedisClient();

  private getKey(sessionId: string): string {
    return `claudia:session:${sessionId}`;
  }

  async get(sessionId: string): Promise<{ data: SessionData; agent: PlannerAgent } | null> {
    // Try Redis first
    if (this.redis) {
      try {
        const serialized = await this.redis.get(this.getKey(sessionId));
        if (serialized) {
          const data: SessionData = JSON.parse(serialized);

          // Recreate PlannerAgent from state
          const apiKey = process.env.ANTHROPIC_API_KEY!;
          const agent = new PlannerAgent(apiKey);

          // Restore agent state if available
          if (data.plannerState) {
            agent.restoreState(data.plannerState);
          }

          return { data, agent };
        }
      } catch (error) {
        console.error('❌ Redis get error:', error);
        // Fall through to memory store
      }
    }

    // Fallback to memory
    return memoryStore.get(sessionId) || null;
  }

  async set(sessionId: string, data: SessionData, agent: PlannerAgent): Promise<void> {
    // Extract serializable agent state
    const plannerState = {
      conversationHistory: agent.getConversationHistory() || [],
      requirements: agent.getFinalRequirements(),
      questionCount: agent.getQuestionCount(),
    };

    const sessionData: SessionData = {
      ...data,
      plannerState,
      lastActivityAt: Date.now(),
    };

    // Try Redis first
    if (this.redis) {
      try {
        await this.redis.setex(
          this.getKey(sessionId),
          SESSION_TTL,
          JSON.stringify(sessionData)
        );
      } catch (error) {
        console.error('❌ Redis set error:', error);
        // Fall through to memory store
      }
    }

    // Always update memory store as backup
    memoryStore.set(sessionId, { data: sessionData, agent });
  }

  async delete(sessionId: string): Promise<void> {
    if (this.redis) {
      try {
        await this.redis.del(this.getKey(sessionId));
      } catch (error) {
        console.error('❌ Redis delete error:', error);
      }
    }

    memoryStore.delete(sessionId);
  }

  async exists(sessionId: string): Promise<boolean> {
    if (this.redis) {
      try {
        const exists = await this.redis.exists(this.getKey(sessionId));
        return exists === 1;
      } catch (error) {
        console.error('❌ Redis exists error:', error);
      }
    }

    return memoryStore.has(sessionId);
  }

  async updateActivity(sessionId: string): Promise<void> {
    if (this.redis) {
      try {
        // Refresh TTL
        await this.redis.expire(this.getKey(sessionId), SESSION_TTL);
      } catch (error) {
        console.error('❌ Redis updateActivity error:', error);
      }
    }
  }
}

// Export singleton instance
export const sessionStore = new SessionStore();
