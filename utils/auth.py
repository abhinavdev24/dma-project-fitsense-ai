"""
FitSense AI Dashboard - Authentication Module
================================================
Handles user authentication using Google OAuth.
"""

import streamlit as st
import os
from datetime import datetime, timedelta
from pathlib import Path


def init_auth_state():
    """Initialize authentication session state."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None


def check_authentication():
    """Check if user is authenticated."""
    init_auth_state()
    return st.session_state.authenticated


def login_user(email: str, name: str):
    """Log in a user."""
    st.session_state.authenticated = True
    st.session_state.user_email = email
    st.session_state.user_name = name
    st.session_state.login_time = datetime.now()


def logout_user():
    """Log out the current user."""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.login_time = None


def get_user_info():
    """Get current user information."""
    if check_authentication():
        return {
            "email": st.session_state.user_email,
            "name": st.session_state.user_name,
            "login_time": st.session_state.login_time
        }
    return None


def get_allowed_emails():
    """Get list of allowed emails from environment variable."""
    allowed = os.getenv("ALLOWED_EMAILS", "")
    if allowed:
        return [email.strip() for email in allowed.split(",")]
    return []


def is_email_allowed(email: str) -> bool:
    """Check if email is in the allowed list."""
    allowed = get_allowed_emails()
    if not allowed:  # If no allowed list, allow all
        return True
    return email in allowed


def show_login_page():
    """Render the login page with Google OAuth."""
    init_auth_state()
    
    # Check if already authenticated
    if check_authentication():
        st.rerun()
    
    # Custom CSS for glassmorphism login card
    st.markdown("""
    <style>
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 80vh;
            padding: 2rem;
        }
        
        .login-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 3rem;
            max-width: 450px;
            width: 100%;
            text-align: center;
            box-shadow: 
                0 25px 50px -12px rgba(0, 0, 0, 0.5),
                0 0 0 1px rgba(255, 255, 255, 0.05);
        }
        
        .login-logo {
            margin-bottom: 1rem;
            display: flex;
            justify-content: center;
        }

        .login-logo img {
            width: 100px;
            height: auto;
        }
        
        .login-title {
            font-size: 2rem;
            font-weight: 700;
            color: #F1F5F9;
            margin-bottom: 0.5rem;
        }
        
        .login-subtitle {
            font-size: 1rem;
            color: #94A3B8;
            margin-bottom: 2rem;
        }
        
        .login-divider {
            border: none;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            margin: 2rem 0;
        }
        
        .login-footer {
            font-size: 0.8rem;
            color: #64748B;
            margin-top: 1.5rem;
        }
        
        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 1rem 2rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
        }
        
        .bg-decoration {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: -1;
            overflow: hidden;
        }
        
        .bg-circle {
            position: absolute;
            border-radius: 50%;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
            animation: float 20s ease-in-out infinite;
        }
        
        .bg-circle:nth-child(1) {
            width: 600px;
            height: 600px;
            top: -200px;
            right: -200px;
        }
        
        .bg-circle:nth-child(2) {
            width: 400px;
            height: 400px;
            bottom: -100px;
            left: -100px;
            animation-delay: -5s;
        }
        
        .bg-circle:nth-child(3) {
            width: 300px;
            height: 300px;
            top: 50%;
            left: 50%;
            animation-delay: -10s;
        }
        
        @keyframes float {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            25% { transform: translate(50px, 50px) rotate(90deg); }
            50% { transform: translate(0, 100px) rotate(180deg); }
            75% { transform: translate(-50px, 50px) rotate(270deg); }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Background decoration
    st.markdown("""
    <div class="bg-decoration">
        <div class="bg-circle"></div>
        <div class="bg-circle"></div>
        <div class="bg-circle"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Login card
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    # Get logo path
    logo_path = Path(__file__).parent.parent / "assets" / "logo.svg"

    st.markdown(f"""
    <div class="login-card">
        <div class="login-logo"><img src="assets/logo.svg" alt="FitSense AI Logo"></div>
        <h1 class="login-title">FitSense AI</h1>
        <p class="login-subtitle">Health & Fitness Analytics Dashboard</p>

        <hr class="login-divider">

        <p style="color: #94A3B8; margin-bottom: 1rem;">Sign in to access your analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Google OAuth Button
    google_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    
    if google_client_id:
        # Use streamlit-google-auth if configured
        try:
            from streamlit_google_auth import Authenticate
            st.warning("streamlit-google-auth integration not yet configured. Please set up OAuth credentials.")
        except ImportError:
            pass
    
    # Demo login for development
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    
    if demo_mode:
        st.info("🔧 Demo Mode: Click below to login without OAuth")
        if st.button("🚀 Demo Login", type="primary"):
            login_user("demo@fitsense.ai", "Demo User")
            st.rerun()
    else:
        st.warning("""
        🔐 **OAuth Setup Required**
        
        To enable Google Sign-In, set these environment variables:
        
        ```bash
        export GOOGLE_CLIENT_ID="your-client-id"
        export GOOGLE_CLIENT_SECRET="your-client-secret"
        export DEMO_MODE="true"  # For development only
        ```
        
        For quick testing, you can also set:
        ```bash
        export DEMO_MODE="true"
        ```
        """)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔧 Demo Mode", type="secondary", width='stretch'):
                os.environ["DEMO_MODE"] = "true"
                login_user("demo@fitsense.ai", "Demo User")
                st.rerun()
        with col2:
            st.button("🔐 Sign in with Google", disabled=True, width='stretch')
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-footer">
        <p>By signing in, you agree to our Terms of Service and Privacy Policy</p>
    </div>
    """, unsafe_allow_html=True)


def require_auth():
    """Decorator/guard to require authentication for pages."""
    if not check_authentication():
        show_login_page()
        st.stop()


def show_logout_button():
    """Show a logout button in the sidebar."""
    if check_authentication():
        user_info = get_user_info()
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"""
        <div class="user-info">
            <div class="user-name">{user_info['name']}</div>
            <div class="user-email">{user_info['email']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("🚪 Logout", width='stretch'):
            logout_user()
            st.rerun()
