"""
Redis Connection Module

Provides Redis client for caching and real-time meeting state.
"""

from typing import Any, Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from src.shared.config import get_settings


class RedisClient:
    """
    Redis client wrapper with connection pooling.

    Provides methods for common Redis operations with
    automatic JSON serialization/deserialization.
    """

    def __init__(self, client: Redis):
        self._client = client

    @property
    def client(self) -> Redis:
        """Get the underlying Redis client."""
        return self._client

    # String operations
    async def get(self, key: str) -> Optional[str]:
        """Get a string value."""
        return await self._client.get(key)

    async def set(
        self,
        key: str,
        value: str,
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """Set a string value with optional expiration."""
        return await self._client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)

    async def delete(self, *keys: str) -> int:
        """Delete one or more keys."""
        return await self._client.delete(*keys)

    async def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        return await self._client.exists(*keys)

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on a key."""
        return await self._client.expire(key, seconds)

    async def ttl(self, key: str) -> int:
        """Get time to live for a key."""
        return await self._client.ttl(key)

    # Hash operations
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get a hash field value."""
        return await self._client.hget(name, key)

    async def hset(self, name: str, key: str, value: str) -> int:
        """Set a hash field value."""
        return await self._client.hset(name, key, value)

    async def hgetall(self, name: str) -> dict:
        """Get all hash fields and values."""
        return await self._client.hgetall(name)

    async def hdel(self, name: str, *keys: str) -> int:
        """Delete hash fields."""
        return await self._client.hdel(name, *keys)

    # List operations
    async def lpush(self, name: str, *values: str) -> int:
        """Push values to the head of a list."""
        return await self._client.lpush(name, *values)

    async def rpush(self, name: str, *values: str) -> int:
        """Push values to the tail of a list."""
        return await self._client.rpush(name, *values)

    async def lpop(self, name: str) -> Optional[str]:
        """Pop from the head of a list."""
        return await self._client.lpop(name)

    async def rpop(self, name: str) -> Optional[str]:
        """Pop from the tail of a list."""
        return await self._client.rpop(name)

    async def lrange(self, name: str, start: int, end: int) -> list:
        """Get a range of list elements."""
        return await self._client.lrange(name, start, end)

    # Pub/Sub operations
    async def publish(self, channel: str, message: str) -> int:
        """Publish a message to a channel."""
        return await self._client.publish(channel, message)

    def pubsub(self):
        """Get a pubsub instance."""
        return self._client.pubsub()

    # Meeting-specific methods
    async def set_meeting_state(
        self, meeting_id: str, state: dict, ttl: int = 3600
    ) -> bool:
        """Store meeting state with TTL."""
        import json

        key = f"meeting:active:{meeting_id}"
        return await self.set(key, json.dumps(state), ex=ttl)

    async def get_meeting_state(self, meeting_id: str) -> Optional[dict]:
        """Retrieve meeting state."""
        import json

        key = f"meeting:active:{meeting_id}"
        data = await self.get(key)
        return json.loads(data) if data else None

    async def delete_meeting_state(self, meeting_id: str) -> int:
        """Delete meeting state."""
        key = f"meeting:active:{meeting_id}"
        return await self.delete(key)

    async def set_verification_pending(
        self, verification_id: str, data: dict, ttl: int = 300
    ) -> bool:
        """Store pending verification with TTL."""
        import json

        key = f"verification:pending:{verification_id}"
        return await self.set(key, json.dumps(data), ex=ttl)

    async def get_verification_pending(self, verification_id: str) -> Optional[dict]:
        """Retrieve pending verification."""
        import json

        key = f"verification:pending:{verification_id}"
        data = await self.get(key)
        return json.loads(data) if data else None

    async def close(self) -> None:
        """Close the Redis connection."""
        await self._client.close()


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


async def get_redis() -> RedisClient:
    """
    Get or create the Redis client.

    Returns:
        RedisClient: The Redis client instance.
    """
    global _redis_client

    if _redis_client is None:
        settings = get_settings()
        client = redis.from_url(
            settings.redis.url,
            max_connections=settings.redis.max_connections,
            decode_responses=settings.redis.decode_responses,
            socket_timeout=settings.redis.socket_timeout,
            socket_connect_timeout=settings.redis.socket_connect_timeout,
        )
        _redis_client = RedisClient(client)

    return _redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global _redis_client

    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
