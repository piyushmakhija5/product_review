/**
 * Redis Client - Simple connection management
 */

import Redis from 'ioredis';

let redisClient: Redis | null = null;

export function getRedisClient(): Redis | null {
  if (redisClient) {
    return redisClient;
  }

  // Only initialize if Redis URL is provided
  const redisUrl = process.env.REDIS_URL;
  if (!redisUrl) {
    console.warn('⚠️  REDIS_URL not configured - using in-memory fallback');
    return null;
  }

  try {
    redisClient = new Redis(redisUrl, {
      retryStrategy(times) {
        const delay = Math.min(times * 50, 2000);
        return delay;
      },
      maxRetriesPerRequest: 3,
    });

    redisClient.on('error', (err) => {
      console.error('❌ Redis error:', err);
    });

    redisClient.on('connect', () => {
      console.log('✅ Redis connected');
    });

    return redisClient;
  } catch (error) {
    console.error('❌ Failed to initialize Redis:', error);
    return null;
  }
}

export async function closeRedis() {
  if (redisClient) {
    await redisClient.quit();
    redisClient = null;
  }
}
