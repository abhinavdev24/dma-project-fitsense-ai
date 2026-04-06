"""
FitSense AI Dashboard - Error Handler Module
=============================================
Centralized error handling and logging.
"""

import streamlit as st
import traceback
import logging
from datetime import datetime
from typing import Optional, Callable, Any
from functools import wraps


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FitSenseAI")


class DashboardError(Exception):
    """Base exception for dashboard errors."""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(DashboardError):
    """Database connection or query errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, error_code="DB_ERROR", details=details)


class AuthenticationError(DashboardError):
    """Authentication/authorization errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, error_code="AUTH_ERROR", details=details)


class ValidationError(DashboardError):
    """Data validation errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, error_code="VALIDATION_ERROR", details=details)


def log_error(error: Exception, context: str = ""):
    """Log an error with context."""
    error_type = type(error).__name__
    error_msg = str(error)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_message = f"[{timestamp}] {error_type} in {context}: {error_msg}"
    
    if isinstance(error, DashboardError) and error.details:
        logger.error(f"{log_message} | Details: {error.details}")
    else:
        logger.error(log_message)
    
    # Log traceback in debug mode
    import os
    if os.getenv("DEBUG", "false").lower() == "true":
        logger.debug(traceback.format_exc())


def show_error_message(error: Exception, context: str = ""):
    """Display a user-friendly error message."""
    log_error(error, context)
    
    error_type = type(error).__name__
    
    if isinstance(error, DatabaseError):
        st.error(f"""
        ⚠️ **Database Error**
        
        Unable to connect to the database. Please check:
        - Database server is running
        - Connection credentials are correct
        - Network connectivity
        
        If the problem persists, contact support.
        """)
    elif isinstance(error, AuthenticationError):
        st.error(f"""
        🔐 **Authentication Error**
        
        You are not authorized to access this resource.
        Please log in again or contact your administrator.
        """)
    elif isinstance(error, ValidationError):
        st.error(f"""
        ⚠️ **Validation Error**
        
        The provided data is invalid: {error.message}
        """)
    else:
        st.error(f"""
        ❌ **An Error Occurred**
        
        {error.message}
        
        Please try again or contact support if the problem persists.
        """)


def show_success_message(message: str):
    """Display a success message."""
    st.success(f"✅ {message}")


def show_info_message(message: str):
    """Display an info message."""
    st.info(f"ℹ️ {message}")


def show_warning_message(message: str):
    """Display a warning message."""
    st.warning(f"⚠️ {message}")


def error_boundary(func: Callable) -> Callable:
    """
    Decorator to wrap functions with error handling.
    
    Usage:
        @error_boundary
        def my_function():
            # code that might fail
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except DashboardError as e:
            show_error_message(e, context=func.__name__)
            return None
        except Exception as e:
            show_error_message(e, context=func.__name__)
            return None
    return wrapper


def handle_db_error(func: Callable) -> Callable:
    """
    Decorator specifically for database operations.
    
    Usage:
        @handle_db_error
        def fetch_data():
            # database code
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            db_error = DatabaseError(
                message=f"Database operation failed: {str(e)}",
                details={"function": func.__name__}
            )
            show_error_message(db_error, context=func.__name__)
            return None
    return wrapper


class LoadingState:
    """Context manager for showing loading states."""
    
    def __init__(self, message: str = "Loading..."):
        self.message = message
        self.container = None
    
    def __enter__(self):
        self.container = st.empty()
        with self.container:
            return st.spinner(self.message)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.container:
            self.container.empty()


def with_loading_state(message: str = "Loading..."):
    """
    Decorator to show loading state during function execution.
    
    Usage:
        @with_loading_state("Fetching data...")
        def fetch_data():
            # code
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with st.spinner(message):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    show_error_message(e, context=func.__name__)
                    return None
        return wrapper
    return decorator


def retry_operation(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator to retry failed operations.
    
    Usage:
        @retry_operation(max_attempts=3, delay=1.0)
        def unreliable_function():
            # code that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import time
            
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}"
                        )
            
            raise last_exception
        return wrapper
    return decorator


# Performance monitoring
def log_performance(func: Callable) -> Callable:
    """
    Decorator to log function execution time.
    
    Usage:
        @log_performance
        def slow_function():
            # code
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        import time
        
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.info(
            f"{func.__name__} completed in {execution_time:.3f}s"
        )
        
        # Warn if execution is slow (> 1 second)
        if execution_time > 1.0:
            logger.warning(
                f"{func.__name__} is slow ({execution_time:.3f}s). "
                "Consider optimization."
            )
        
        return result
    return wrapper
