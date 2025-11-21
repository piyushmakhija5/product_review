"""
Simple file-based caching system for scraped product data.
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional
from config import Config


class Cache:
    """Simple file-based cache with TTL support."""

    def __init__(self, cache_dir: Optional[Path] = None, ttl_hours: Optional[int] = None):
        """
        Initialize cache.

        Args:
            cache_dir: Directory for cache files. Defaults to Config.CACHE_DIR
            ttl_hours: Time-to-live in hours. Defaults to Config.CACHE_TTL_HOURS
        """
        self.cache_dir = cache_dir or Config.CACHE_DIR
        self.ttl_hours = ttl_hours or Config.CACHE_TTL_HOURS
        self.enabled = Config.CACHE_ENABLED

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _make_key(self, key: str) -> str:
        """Generate a safe filename from cache key."""
        # Use hash to create a safe filename
        hash_obj = hashlib.md5(key.encode())
        return hash_obj.hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        safe_key = self._make_key(key)
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if not self.enabled:
            return None

        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # Check if expired
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            expires_at = cached_at + timedelta(hours=self.ttl_hours)

            if datetime.now() > expires_at:
                # Cache expired, delete it
                cache_path.unlink()
                return None

            return cache_data['value']

        except (json.JSONDecodeError, KeyError, ValueError):
            # Invalid cache file, delete it
            if cache_path.exists():
                cache_path.unlink()
            return None

    def set(self, key: str, value: Any) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        cache_path = self._get_cache_path(key)

        cache_data = {
            'key': key,
            'value': value,
            'cached_at': datetime.now().isoformat(),
            'ttl_hours': self.ttl_hours
        }

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, default=str)
            return True
        except (TypeError, IOError) as e:
            if Config.DEBUG:
                print(f"Cache write error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete a cache entry.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        cache_path = self._get_cache_path(key)

        if cache_path.exists():
            cache_path.unlink()
            return True

        return False

    def clear_all(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except IOError:
                pass

        return count

    def clear_expired(self) -> int:
        """
        Clear expired cache entries.

        Returns:
            Number of expired entries deleted
        """
        count = 0

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                cached_at = datetime.fromisoformat(cache_data['cached_at'])
                ttl_hours = cache_data.get('ttl_hours', self.ttl_hours)
                expires_at = cached_at + timedelta(hours=ttl_hours)

                if datetime.now() > expires_at:
                    cache_file.unlink()
                    count += 1

            except (json.JSONDecodeError, KeyError, ValueError, IOError):
                # Invalid cache file, delete it
                try:
                    cache_file.unlink()
                    count += 1
                except IOError:
                    pass

        return count

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats
        """
        total = 0
        expired = 0
        total_size = 0

        for cache_file in self.cache_dir.glob("*.json"):
            total += 1
            total_size += cache_file.stat().st_size

            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                cached_at = datetime.fromisoformat(cache_data['cached_at'])
                ttl_hours = cache_data.get('ttl_hours', self.ttl_hours)
                expires_at = cached_at + timedelta(hours=ttl_hours)

                if datetime.now() > expires_at:
                    expired += 1

            except (json.JSONDecodeError, KeyError, ValueError, IOError):
                expired += 1

        return {
            'total_entries': total,
            'expired_entries': expired,
            'valid_entries': total - expired,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir),
            'enabled': self.enabled
        }


def make_cache_key(*args, **kwargs) -> str:
    """
    Create a cache key from arguments.

    Usage:
        key = make_cache_key('amazon', 'laptop', budget=1500)
    """
    parts = [str(arg) for arg in args]
    parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return "|".join(parts)
