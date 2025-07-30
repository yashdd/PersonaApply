import streamlit as st
import requests
import os
from dotenv import load_dotenv
from app.sidebar import show_sidebar
import pyperclip
from datetime import datetime

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
show_sidebar()
st.header("✨ Content Generation")

if st.session_state.get("redirect_to_content_gen"):
    st.session_state.redirect_to_content_gen = False
    st.experimental_rerun()

if not st.session_state.get("authenticated"):
    st.warning("⚠️ Please sign in first!")
    st.stop()

st.write("Generate personalized content based on your profile and documents.")

# Initialize form values in session state if not present
if 'form_content_type' not in st.session_state:
    st.session_state.form_content_type = "cover_letter"
if 'form_job_description' not in st.session_state:
    st.session_state.form_job_description = ""
if 'form_target_company' not in st.session_state:
    st.session_state.form_target_company = ""
if 'form_target_role' not in st.session_state:
    st.session_state.form_target_role = ""
if 'form_additional_context' not in st.session_state:
    st.session_state.form_additional_context = ""
if 'form_tone' not in st.session_state:
    st.session_state.form_tone = "professional"

content_type = st.selectbox(
    "Content Type", 
    ["cover_letter", "cold_email", "linkedin_message"], 
    format_func=lambda x: x.replace("_", " ").title(),
    key="content_type_select",
    index=["cover_letter", "cold_email", "linkedin_message"].index(st.session_state.form_content_type)
)

job_description = st.text_area(
    "Job Description or Situation", 
    height=200,
    key="job_description_text",
    value=st.session_state.form_job_description
)

col1, col2 = st.columns(2)
with col1:
    target_company = st.text_input(
        "Target Company (optional)",
        key="target_company_input",
        value=st.session_state.form_target_company
    )
    tone = st.selectbox(
        "Tone", 
        ["professional", "friendly", "formal", "casual"],
        key="tone_select",
        index=["professional", "friendly", "formal", "casual"].index(st.session_state.form_tone)
    )
with col2:
    target_role = st.text_input(
        "Target Role (optional)",
        key="target_role_input", 
        value=st.session_state.form_target_role
    )
    additional_context = st.text_area(
        "Additional Context (optional)",
        key="additional_context_text",
        value=st.session_state.form_additional_context
    )

if st.button("Generate Content", type="primary"):
    if not job_description.strip():
        st.error("❌ Please provide a job description or situation.")
    else:
        # Store form values in session state
        st.session_state.form_content_type = content_type
        st.session_state.form_job_description = job_description
        st.session_state.form_target_company = target_company
        st.session_state.form_target_role = target_role
        st.session_state.form_additional_context = additional_context
        st.session_state.form_tone = tone
        
        try:
            request_data = {
                "content_type": content_type,
                "job_description": job_description,
                "target_company": target_company,
                "target_role": target_role,
                "additional_context": additional_context,
                "tone": tone
            }
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            response = requests.post(f"{API_BASE_URL}/content/generate", json=request_data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                
                # Store the generated content and details in session state
                st.session_state.generated_content = result["generated_content"]
                st.session_state.content_type = result["content_type"]
                st.session_state.tone = tone
                st.session_state.generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.session_state.prompt_used = result.get("prompt_used", "")
                st.session_state.tokens_used = result.get("tokens_used", 0)
                
                st.success("✅ Content generated successfully!")
                st.rerun()
            else:
                st.error(f"❌ Error generating content: {response.text}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display generated content if available in session state
if hasattr(st.session_state, 'generated_content') and st.session_state.generated_content:
    st.subheader("Generated Content")
    
    # Display content in a styled text area
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 4px solid #1f77b4;">
        <pre style="white-space: pre-wrap; font-family: 'Courier New', monospace; margin: 0;">{st.session_state.generated_content}</pre>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 Copy to Clipboard", key="copy_button", type="secondary"):
            try:
                pyperclip.copy(st.session_state.generated_content)
                st.success("✅ Copied to clipboard!")
            except Exception as e:
                st.error("❌ Could not copy to clipboard")
    
    with col2:
        # Save as file functionality using download button
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{st.session_state.content_type}_{timestamp}.txt"
        
        st.download_button(
            label="💾 Save as File",
            data=st.session_state.generated_content,
            file_name=filename,
            mime="text/plain",
            key="download_button"
        )
    
    with col3:
        if st.button("🔄 Generate Again", key="generate_again", type="secondary"):
            # Regenerate content with the same parameters
            try:
                request_data = {
                    "content_type": st.session_state.content_type,
                    "job_description": job_description,
                    "target_company": target_company,
                    "target_role": target_role,
                    "additional_context": additional_context,
                    "tone": st.session_state.tone
                }
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                response = requests.post(f"{API_BASE_URL}/content/generate", json=request_data, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    
                    # Update the generated content in session state
                    st.session_state.generated_content = result["generated_content"]
                    st.session_state.generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    st.session_state.prompt_used = result.get("prompt_used", "")
                    st.session_state.tokens_used = result.get("tokens_used", 0)
                    
                    st.success("✅ Content regenerated successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Error regenerating content: {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col4:
        if st.button("🗑️ Clear", key="clear_button", type="secondary"):
            # Clear the generated content from session state
            
            if 'generated_content' in st.session_state:
                del st.session_state.generated_content
            if 'content_type' in st.session_state:
                del st.session_state.content_type
            if 'tone' in st.session_state:
                del st.session_state.tone
            if 'generation_time' in st.session_state:
                del st.session_state.generation_time
            if 'prompt_used' in st.session_state:
                del st.session_state.prompt_used
            if 'tokens_used' in st.session_state:
                del st.session_state.tokens_used
            
            # Clear form fields from session state
            if 'form_job_description' in st.session_state:
                del st.session_state.form_job_description
            if 'form_target_company' in st.session_state:
                del st.session_state.form_target_company
            if 'form_target_role' in st.session_state:
                del st.session_state.form_target_role
            if 'form_additional_context' in st.session_state:
                del st.session_state.form_additional_context
            if 'form_tone' in st.session_state:
                del st.session_state.form_tone
            if 'form_content_type' in st.session_state:
                del st.session_state.form_content_type
            
            st.rerun()
    # Show generation details in expander
    with st.expander("🔍 Generation Details"):
        st.write(f"**Content Type:** {st.session_state.content_type.replace('_', ' ').title()}")
        st.write(f"**Tone Used:** {st.session_state.tone.title()}")
        if st.session_state.tokens_used:
            st.write(f"**Tokens Used:** {st.session_state.tokens_used}")
        st.write(f"**Generated:** {st.session_state.generation_time}")
        
        # Show the prompt used (for debugging/transparency)
        with st.expander("📝 Prompt Used"):
            st.text(st.session_state.prompt_used)

