import streamlit as st
import requests
import os
from dotenv import load_dotenv
from app.sidebar import show_sidebar

# Hide default page navigation with CSS
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

load_dotenv()
FIREBASE_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")
show_sidebar()
st.header("🔐 Sign In")
with st.form("signin_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Sign In")
    if submitted:
        if not email or not password:
            st.error("❌ Please provide both email and password.")
        else:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
            payload = {"email": email, "password": password, "returnSecureToken": True}
            resp = requests.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.token = data["idToken"]
                st.session_state.user = {"email": email, "uid": data.get("localId", "")}
                st.session_state.authenticated = True
                st.success("✅ Authentication successful!")
                st.rerun()
            else:
                st.error(f"Login failed: {resp.json().get('error', {}).get('message', 'Unknown error')}") 