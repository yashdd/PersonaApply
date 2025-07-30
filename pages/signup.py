import streamlit as st
from firebase_admin import auth, credentials
from google.cloud import firestore
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
import firebase_admin
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

# Firebase/Firestore credentials setup
cred_dict = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID", "personaapply"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL", ""),
    "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL", "")
}

# Initialize Firebase Admin SDK if not already initialized
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'projectId': cred_dict["project_id"]
    })

firestore_creds = service_account.Credentials.from_service_account_info(cred_dict)
db = firestore.Client(credentials=firestore_creds, project=cred_dict["project_id"])

# Ensure keys exist
for key in ["signup_name", "signup_email", "signup_password", "signup_confirm_password", "signup_age"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "signup_age" else 0

# Clear fields and show success message if signup was successful
if st.session_state.get("signup_success"):
    st.session_state.signup_name = ""
    st.session_state.signup_email = ""
    st.session_state.signup_password = ""
    st.session_state.signup_confirm_password = ""
    st.session_state.signup_age = 0
    st.session_state.signup_success = False
    st.success("✅ You have successfully signed up! Please select 'Content Generation' from the sidebar to continue.")

show_sidebar()

st.header("📝 Sign Up")
with st.form("signup_form"):
    name = st.text_input("Full Name", key="signup_name")
    age = st.number_input("Age", min_value=0, max_value=120, step=1, key="signup_age")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
    submitted = st.form_submit_button("Sign Up")
    if submitted:
        if not name or not email or not password or not confirm_password:
            st.error("❌ Please fill in all fields.")
        elif password != confirm_password:
            st.error("❌ Passwords do not match.")
        else:
            try:
                user = auth.create_user(
                    email=email,
                    password=password,
                    display_name=name
                )
                db.collection("users").document(user.uid).set({
                    "uid": user.uid,
                    "email": email,
                    "name": name,
                    "age": age,
                    "created_at": SERVER_TIMESTAMP
                })
                st.session_state.user = {"email": email, "uid": user.uid, "name": name, "age": age}
                st.session_state.authenticated = True
                st.session_state.signup_success = True
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error creating user: {str(e)}") 