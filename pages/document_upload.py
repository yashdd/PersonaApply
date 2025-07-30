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
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

load_dotenv()
API_BASE_URL = "http://localhost:8000"
if "token" not in st.session_state:
    st.session_state.token = ""
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = {}
    
show_sidebar()
st.header("📄 Document Upload")

if not st.session_state.get("authenticated"):
    st.warning("⚠️ Please sign in first!")
    st.stop()

st.write("Upload your professional documents or add links for personalized content generation.")

# Choose between file upload or link
upload_type = st.radio("Choose upload type:", ["📁 Upload File", "🔗 Add Link"])

if upload_type == "📁 Upload File":
    # File upload section
    st.subheader("📁 File Upload")
    
    # Expanded document types
    doc_type = st.selectbox(
        "Document Type", 
        [
            "resume", 
            "cover_letter",  
            "portfolio", 
            "certificate", 
            "project", 
            "publication", 
            "other"
        ], 
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    uploaded_file = st.file_uploader("Choose a file", type=['txt', 'pdf', 'docx', 'md', 'rtf'])
    
    if uploaded_file and st.button("Upload Document", type="primary"):
        try:
            files = {"file": uploaded_file}
            data = {"document_type": doc_type}
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            response = requests.post(f"{API_BASE_URL}/user/documents/upload", files=files, data=data, headers=headers)
            if response.status_code == 200:
                st.success("✅ Document uploaded successfully!")
                st.rerun()
            else:
                st.error(f"❌ Error uploading document: {response.text}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

else:
    # Link section
    st.subheader("🔗 Add Link")
    
    # Link types
    link_type = st.selectbox(
        "Link Type", 
        [
            "linkedin", 
            "github", 
            "portfolio", 
            "other"
        ], 
        format_func=lambda x: x.title()
    )
    
    link_url = st.text_input("Enter URL", placeholder="https://...")
    link_description = st.text_area("Description (optional)", placeholder="Brief description of this link...")
    
    if link_url and st.button("Add Link", type="primary"):
        if not link_url.startswith(('http://', 'https://')):
            st.error("❌ Please enter a valid URL starting with http:// or https://")
        else:
            try:
                # For links, we'll create a text file with the URL and description
                link_content = f"URL: {link_url}\nType: {link_type}\nDescription: {link_description or 'No description provided'}"
                
                # Create a temporary file-like object
                import io
                link_file = io.StringIO(link_content)
                link_file.name = f"{link_type}_link.txt"
                
                files = {"file": link_file}
                data = {"document_type": link_type}
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                response = requests.post(f"{API_BASE_URL}/user/documents/upload", files=files, data=data, headers=headers)
                if response.status_code == 200:
                    st.success("✅ Link added successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Error adding link: {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Display documents with improved UI
st.subheader("Your Documents & Links")
try:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{API_BASE_URL}/user/documents", headers=headers)
    if response.status_code == 200:
        documents = response.json()
        if documents:
            for i, doc in enumerate(documents):
                # Determine icon and color based on document type
                if doc['document_type'] in ['linkedin', 'github', 'portfolio']:
                    icon = "🔗"
                    color = "blue"
                else:
                    icon = "📄"
                    color = "green"
                
                # Create a container for each document
                with st.container():
                    # Use columns with more space for document info, less for button
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin: 5px 0;">
                            <strong>{icon} {doc['filename']}</strong><br>
                            <small style="color: {color};">{doc['document_type'].replace('_', ' ').title()}</small><br>
                            <small style="color: #666;">Uploaded: {doc['created_at'][:10]}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # Delete button aligned with document info
                        if st.button("🗑️", key=f"delete_{doc['document_id']}", type="secondary", help="Delete this document"):
                            delete_response = requests.delete(f"{API_BASE_URL}/user/documents/{doc['document_id']}", headers=headers)
                            if delete_response.status_code == 200:
                                st.success("✅ Deleted!")
                                st.rerun()
                            else:
                                st.error("❌ Error deleting")
                
                # Add some spacing between documents
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("📝 No documents or links uploaded yet.")
    else:
        st.error("❌ Error fetching documents")
except Exception as e:
    st.error(f"❌ Error: {str(e)}") 