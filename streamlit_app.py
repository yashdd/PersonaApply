import streamlit as st
from PIL import Image
from app.sidebar import show_sidebar

# Configure page to hide default sidebar
st.set_page_config(
    page_title="PersonaApply",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default page navigation with CSS
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Check authentication status
is_authenticated = st.session_state.get("authenticated", False)

# Custom Sidebar Navigation
# with st.sidebar:
#     st.title("🚀 PersonaApply")
    
#     if is_authenticated:
#         # User is logged in - show app navigation and logout
#         st.success(f"✅ {st.session_state.user.get('email', 'User')}")
#         st.markdown("---")
        
#         # App Navigation
#         st.markdown("### 📚 Navigation")
#         if st.button("📄 Document Upload", use_container_width=True):
#             st.switch_page("pages/document_upload.py")
#         if st.button("✏️ Content Generation", use_container_width=True):
#             st.switch_page("pages/content_generation.py")
        
#         st.markdown("---")
        
#         # Logout button
#         if st.button("🚪 Logout", type="secondary", use_container_width=True):
#             # Clear session state
#             st.session_state.authenticated = False
#             st.session_state.user = {}
#             st.session_state.token = ""
#             st.rerun()
#     else:
#         # User is not logged in - show auth options
#         st.info("Please sign in to continue")
#         st.markdown("---")
        
#         if st.button("🔐 Sign In", type="primary", use_container_width=True):
#             st.switch_page("pages/signin.py")
#         if st.button("📝 Sign Up", type="secondary", use_container_width=True):
#             st.switch_page("pages/signup.py")

show_sidebar()
# Main Title and Subtitle
st.markdown(
    """
    <h1 style='font-size: 48px; margin-bottom: 0;'>🚀 PersonaApply</h1>
    <h3 style='color: gray; margin-top: 0;'>AI-Powered Personalized Cover Letters & Cold Emails</h3>
    """,
    unsafe_allow_html=True
)

# Authentication Status and Logout
if is_authenticated:
    # User is logged in - show welcome and logout
    col1, col2 = st.columns([3, 1])
    with col1:
        user_email = st.session_state.user.get('email', 'User')
        st.success(f"✅ Welcome back, {user_email}!")
    with col2:
        if st.button("🚪 Logout", type="secondary"):
            # Clear session state
            st.session_state.authenticated = False
            st.session_state.user = {}
            st.session_state.token = ""
            st.rerun()
    
    st.markdown("---")
    st.markdown(
        """
        <div style='font-size:18px; line-height:1.6;'>
            <b>Ready to generate personalized content!</b><br>
            Use the sidebar to upload documents and generate cover letters, cold emails, or LinkedIn messages.
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    # User is not logged in - show sign in/up options
    st.markdown("---")
    st.markdown(
        """
        <div style='font-size:18px; line-height:1.6;'>
            <b>Welcome to PersonaApply!</b><br>
            Please sign in or sign up to get started with personalized content generation.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Sign In/Sign Up buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Sign In", type="primary", use_container_width=True):
            st.switch_page("pages/signin.py")
    with col2:
        if st.button("📝 Sign Up", type="secondary", use_container_width=True):
            st.switch_page("pages/signup.py")

# Key Features
st.markdown("### 🔑 Key Features")
st.markdown(
    """
    - 📄 Upload Resume, Past Letters, or Job Descriptions  
    - 🤖 AI-Powered Retrieval-Augmented Generation (RAG) for context-aware content  
    - ✍️ Instant, Personalized Output: Cover Letters & Emails  
    - 🔒 All data is private and stored securely per user
    """
)

# Navigation Instructions
st.markdown("---")
if is_authenticated:
    st.markdown("### 📚 Get Started:")
    st.markdown(
        """
        Use the sidebar to navigate:
        - 📂 **Document Upload**: Upload your resume or previous letters  
        - ✏️ **Generate Content**: Describe your job/posting and generate output  
        """
    )
else:
    st.markdown("### 📚 How it works:")
    st.markdown(
        """
        1. **Sign up** for an account
        2. **Upload documents** (resume, LinkedIn, etc.) for context
        3. **Generate content** (cover letters, cold emails, LinkedIn messages)
        4. **Get personalized** results based on your background
        """
    )

# Footer
st.markdown("---")
st.markdown(
    "<center>Made with ❤️ using Streamlit & FastAPI | © 2025 PersonaApply</center>",
    unsafe_allow_html=True
)
