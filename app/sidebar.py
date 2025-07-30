import streamlit as st

def show_sidebar():
    is_authenticated = st.session_state.get("authenticated", False)
    with st.sidebar:
        st.title("🚀 PersonaApply")
        if is_authenticated:
            st.success(f"✅ {st.session_state.user.get('email', 'User')}")
            st.markdown("---")
            st.markdown("### 📚 Navigation")
            if st.button("📄 Upload Docs", use_container_width=True):
                st.switch_page("pages/document_upload.py")
            if st.button("✏️ Content Generation", use_container_width=True):
                st.switch_page("pages/content_generation.py")
            st.markdown("---")
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user = {}
                st.session_state.token = ""
                st.rerun()
        else:
            st.info("Please sign in to continue")
            st.markdown("---")
            if st.button("🔐 Sign In", type="primary", use_container_width=True):
                st.switch_page("pages/signin.py")
            if st.button("📝 Sign Up", type="secondary", use_container_width=True):
                st.switch_page("pages/signup.py")