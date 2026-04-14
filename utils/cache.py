"""
FitSense AI Dashboard - Cache Module
=====================================
Caching utilities for query results.
"""

import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Callable, Any
from functools import wraps
import os


class QueryCache:
    """
    Simple in-memory cache for query results.
    """

    def __init__(self, default_ttl: int = 300):  # 5 minutes default TTL
        self.default_ttl = default_ttl
        self._cache = {}

    def _make_key(self, query: str, params: tuple = ()) -> str:
        """Generate a cache key from query and parameters."""
        key_string = f"{query}:{params}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, query: str, params: tuple = ()) -> Optional[pd.DataFrame]:
        """Get cached result if available and not expired."""
        key = self._make_key(query, params)

        if key in self._cache:
            entry = self._cache[key]
            if datetime.now() < entry["expires_at"]:
                return entry["data"]
            else:
                # Expired, remove from cache
                del self._cache[key]

        return None

    def set(
        self,
        query: str,
        data: pd.DataFrame,
        params: tuple = (),
        ttl: Optional[int] = None,
    ) -> None:
        """Store result in cache with TTL."""
        key = self._make_key(query, params)
        ttl = ttl or self.default_ttl

        self._cache[key] = {
            "data": data,
            "expires_at": datetime.now() + timedelta(seconds=ttl),
            "created_at": datetime.now(),
        }

    def invalidate(self, query: str = None, params: tuple = None) -> None:
        """Invalidate cache entries."""
        if query is None:
            # Clear all cache
            self._cache.clear()
        elif params is None:
            # Invalidate all entries for this query
            key_prefix = self._make_key(query, ())
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(key_prefix)]
            for key in keys_to_delete:
                del self._cache[key]
        else:
            # Invalidate specific entry
            key = self._make_key(query, params)
            if key in self._cache:
                del self._cache[key]

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_entries = len(self._cache)
        expired_entries = sum(
            1 for entry in self._cache.values() if datetime.now() >= entry["expires_at"]
        )

        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired_entries,
            "expired_entries": expired_entries,
            "default_ttl": self.default_ttl,
        }


# Global cache instance
_query_cache = QueryCache()


def get_cache() -> QueryCache:
    """Get the global cache instance."""
    return _query_cache


def cached_query(ttl: int = 300, cache_key: str = None):
    """
    Decorator to cache query results.

    Usage:
        @cached_query(ttl=600)
        def get_user_count():
            return pd.read_sql("SELECT COUNT(*) FROM users", conn)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Check if caching is disabled
            if os.getenv("DISABLE_CACHE", "false").lower() == "true":
                return func(*args, **kwargs)

            # Generate cache key
            key = cache_key or f"{func.__name__}:{args}:{kwargs}"
            cache_key_hash = hashlib.md5(str(key).encode()).hexdigest()

            # Try to get from cache
            cached_result = _query_cache.get(cache_key_hash)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            if isinstance(result, pd.DataFrame):
                _query_cache.set(cache_key_hash, result, ttl=ttl)

            return result

        return wrapper

    return decorator


def st_cache(ttl: int = 300, allow_output_mutation: bool = False):
    """
    Streamlit cache decorator wrapper.
    Uses Streamlit's native caching when possible.

    Usage:
        @st_cache(ttl=600)
        def expensive_computation():
            # code
            pass
    """
    return st.cache_data(
        ttl=ttl, allow_output_mutation=allow_output_mutation, show_spinner=False
    )


def invalidate_all_caches() -> None:
    """Invalidate all query caches."""
    _query_cache.invalidate()


# Cache management UI
def show_cache_stats():
    """Display cache statistics in Streamlit."""
    stats = _query_cache.get_stats()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Cache Statistics")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Active Entries", stats["active_entries"])
    with col2:
        st.metric("Expired Entries", stats["expired_entries"])

    if st.sidebar.button("🗑️ Clear Cache"):
        invalidate_all_caches()
        st.sidebar.success("Cache cleared!")
        st.rerun()
