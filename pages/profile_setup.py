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
API_BASE_URL = "http://localhost:8000"
show_sidebar()
st.header("👤 Profile Setup")

if not st.session_state.get("authenticated"):
    st.warning("⚠️ Please sign in first!")
    st.stop()

st.success(f"✅ Welcome, {st.session_state.user.get('email', 'User')}!")

with st.form("profile_form"):
    name = st.text_input("Full Name", value=st.session_state.user.get("name", ""))
    title = st.text_input("Professional Title")
    experience_years = st.number_input("Years of Experience", min_value=0, max_value=50)
    github_url = st.text_input("GitHub Profile URL")
    linkedin_url = st.text_input("LinkedIn Profile URL")
    portfolio_url = st.text_input("Portfolio Website URL")
    skills = st.text_area("Skills (comma-separated)")
    summary = st.text_area("Professional Summary", height=100)
    submitted = st.form_submit_button("💾 Save Profile")
    if submitted:
        profile_data = {
            "name": name,
            "title": title,
            "experience_years": experience_years,
            "github_url": github_url,
            "linkedin_url": linkedin_url,
            "portfolio_url": portfolio_url,
            "skills": [skill.strip() for skill in skills.split(",") if skill.strip()],
            "summary": summary
        }
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.put(f"{API_BASE_URL}/user/profile", json=profile_data, headers=headers)
        if response.status_code == 200:
            st.success("✅ Profile updated successfully!")
            st.session_state.user = response.json()
        else:
            st.error(f"❌ Error updating profile: {response.text}")

# Show current profile
st.subheader("📋 Current Profile")
try:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{API_BASE_URL}/user/profile", headers=headers)
    if response.status_code == 200:
        current_profile = response.json()
        st.json(current_profile)
    else:
        st.info("📝 No profile data found. Please complete your profile above.")
except Exception as e:
    st.error(f"❌ Error loading profile: {str(e)}") 