"""
FitSense AI Dashboard - Performance Utilities
==============================================
Performance optimization utilities.
"""

import time
import functools
from typing import Callable, Any, Optional
from datetime import datetime


class PerformanceMonitor:
    """Monitor and track performance metrics."""

    def __init__(self):
        self.metrics = {}

    def record(self, name: str, duration: float, metadata: dict = None):
        """Record a performance metric."""
        if name not in self.metrics:
            self.metrics[name] = []

        self.metrics[name].append(
            {
                "duration": duration,
                "timestamp": datetime.now(),
                "metadata": metadata or {},
            }
        )

    def get_stats(self, name: str) -> dict:
        """Get statistics for a metric."""
        if name not in self.metrics or not self.metrics[name]:
            return {}

        durations = [m["duration"] for m in self.metrics[name]]

        return {
            "count": len(durations),
            "total": sum(durations),
            "average": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations),
        }

    def get_all_stats(self) -> dict:
        """Get statistics for all metrics."""
        return {name: self.get_stats(name) for name in self.metrics}

    def clear(self):
        """Clear all metrics."""
        self.metrics.clear()


# Global performance monitor
_perf_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor."""
    return _perf_monitor


def timed(func: Callable) -> Callable:
    """
    Decorator to time function execution and record metrics.

    Usage:
        @timed
        def slow_function():
            # code
            pass
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            _perf_monitor.record(func.__name__, duration)

    return wrapper


def debounce(wait_ms: int = 300):
    """
    Decorator to debounce function calls.

    Usage:
        @debounce(wait_ms=500)
        def on_change():
            # code
            pass
    """

    def decorator(func: Callable) -> Callable:
        last_call = [0]  # Use list for mutable closure

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time() * 1000  # Convert to milliseconds
            if now - last_call[0] >= wait_ms:
                last_call[0] = now
                return func(*args, **kwargs)

        return wrapper

    return decorator


def memoize(func: Callable) -> Callable:
    """
    Simple memoization decorator for expensive computations.

    Usage:
        @memoize
        def expensive_computation(n):
            # code
            pass
    """
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable key from arguments
        key = str(args) + str(sorted(kwargs.items()))

        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    # Expose cache for inspection/clearing
    wrapper.cache = cache
    wrapper.clear_cache = lambda: cache.clear()

    return wrapper


class LazyLoader:
    """
    Lazy loader for expensive objects that are only created when needed.
    """

    def __init__(self, factory: Callable):
        self.factory = factory
        self._instance = None
        self._loaded = False

    def get(self):
        """Get the lazy-loaded instance."""
        if not self._loaded:
            self._instance = self.factory()
            self._loaded = True
        return self._instance

    def reload(self):
        """Force reload the instance."""
        self._instance = self.factory()
        self._loaded = True
        return self._instance


# Database connection pooling helper
class ConnectionPoolStats:
    """Track database connection pool statistics."""

    def __init__(self):
        self.active_connections = 0
        self.total_connections = 0
        self.connection_errors = 0
        self.query_count = 0
        self.start_time = datetime.now()

    def record_connection(self):
        """Record a new connection."""
        self.active_connections += 1
        self.total_connections += 1

    def record_disconnection(self):
        """Record a disconnection."""
        self.active_connections = max(0, self.active_connections - 1)

    def record_query(self):
        """Record a query execution."""
        self.query_count += 1

    def record_error(self):
        """Record a connection error."""
        self.connection_errors += 1

    def get_stats(self) -> dict:
        """Get current pool statistics."""
        uptime = (datetime.now() - self.start_time).total_seconds()

        return {
            "active_connections": self.active_connections,
            "total_connections": self.total_connections,
            "connection_errors": self.connection_errors,
            "query_count": self.query_count,
            "queries_per_second": self.query_count / uptime if uptime > 0 else 0,
            "uptime_seconds": uptime,
        }


# Global pool stats
_pool_stats = ConnectionPoolStats()


def get_pool_stats() -> ConnectionPoolStats:
    """Get the global pool statistics tracker."""
    return _pool_stats


# Progressive loading helper
class ProgressiveLoader:
    """
    Helper for progressive content loading.
    Shows loading state while content is being prepared.
    """

    def __init__(self, container):
        self.container = container

    def show_loading(self, message: str = "Loading..."):
        """Show loading state."""
        with self.container:
            st = __import__("streamlit")
            st.spinner(message)

    def show_skeleton(self, lines: int = 5):
        """Show skeleton loading animation."""
        with self.container:
            st = __import__("streamlit")
            st.markdown(
                f"""
            <div class="skeleton-container">
                {"".join(['<div class="skeleton-line"></div>' for _ in range(lines)])}
            </div>
            """,
                unsafe_allow_html=True,
            )

    def show_content(self, content_func: Callable, *args, **kwargs):
        """Load and display actual content."""
        with self.container:
            return content_func(*args, **kwargs)


# Performance tips for UI/UX
PERFORMANCE_TIPS = """
### Performance Optimization Tips

1. **Cache Query Results**: Use `@st_cache` or the `cached_query` decorator
2. **Limit Data Rows**: Always use `LIMIT` in SQL queries
3. **Lazy Load Content**: Load below-fold content on scroll
4. **Optimize Charts**: Use `use_container_width=True` for responsive sizing
5. **Connection Pooling**: Reuse database connections
6. **Avoid Re-renders**: Minimize state changes

### UI Polish Checklist

- [ ] Consistent spacing and alignment
- [ ] Smooth transitions (150-300ms)
- [ ] Clear hover and focus states
- [ ] Loading states for async operations
- [ ] Error states with recovery options
- [ ] Empty states with helpful messages
"""
