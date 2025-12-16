import streamlit as st
import tempfile
import os
from jamai import Jamai

# --- CONFIGURATION ---
# REPLACE THESE WITH YOUR ACTUAL CREDENTIALS
PROJECT_ID = "YOUR_PROJECT_ID_HERE"
PAT_KEY = "YOUR_PAT_KEY_HERE"

# Default Table IDs (Change these if your table IDs are different in Jamai)
TABLE_ID_SINGLE = "action-table-single"
TABLE_ID_MULTI = "action-table-multi"

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AERN | AI Emergency Response Navigator",
    page_icon="🚨",
    layout="centered"
)

# --- INITIALIZE JAMAI CLIENT ---
if PROJECT_ID == "YOUR_PROJECT_ID_HERE" or PAT_KEY == "YOUR_PAT_KEY_HERE":
    st.error("🚨 Please insert your actual PROJECT_ID and PAT_KEY in the code first!")
    st.stop()

try:
    jamai = Jamai(token=PAT_KEY, project_id=PROJECT_ID)
except Exception as e:
    st.error(f"Failed to initialize Jamai client: {e}")
    st.stop()

# --- HELPER FUNCTION: SAVE UPLOADED FILE ---
def save_uploaded_file(uploaded_file):
    """
    Helper to save streamlit uploaded file to a temp path 
    so the Jamai SDK can read it.
    """
    try:
        suffix = f".{uploaded_file.name.split('.')[-1]}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error handling file: {e}")
        return None

# --- MAIN APP UI ---
st.title("🚨 AERN")
st.caption("AI Emergency Response Navigator")

# --- TABS FOR DIFFERENT MODES ---
tab1, tab2 = st.tabs(["Single Modality Analysis", "Multi-Modality Fusion"])

# ==========================================
# TAB 1: SINGLE INPUT ACTION TABLE
# ==========================================
with tab1:
    st.header("Single Input Analysis")
    st.info(f"Connected to Table: `{TABLE_ID_SINGLE}`")
    
    input_type = st.radio("Select Input Type", ["Text", "Audio", "Photo"], horizontal=True)
    
    user_data = {}
    ready_to_send = False

    # Input Logic
    if input_type == "Text":
        text_input = st.text_area("Describe the emergency situation:")
        if text_input:
            user_data = {"text": text_input} 
            ready_to_send = True

    elif input_type == "Audio":
        audio_file = st.file_uploader("Upload Audio Recording", type=["mp3", "wav", "m4a"])
        if audio_file:
            path = save_uploaded_file(audio_file)
            # Upload to Jamai to get URI
            with st.spinner("Uploading audio..."):
                uploaded_uri = jamai.file.upload_file(path).uri
            user_data = {"audio": uploaded_uri}
            ready_to_send = True

    elif input_type == "Photo":
        photo_file = st.file_uploader("Upload Scene Photo", type=["jpg", "png", "jpeg"])
        if photo_file:
            path = save_uploaded_file(photo_file)
            st.image(photo_file, caption="Preview", width=300)
            # Upload to Jamai to get URI
            with st.spinner("Uploading photo..."):
                uploaded_uri = jamai.file.upload_file(path).uri
            user_data = {"photo": uploaded_uri}
            ready_to_send = True

    if st.button("Analyze Single Input", disabled=not ready_to_send):
        with st.spinner("Consulting AERN Brain..."):
            try:
                # Add row to Jamai Table
                response = jamai.table.add_row(
                    table_id=TABLE_ID_SINGLE,
                    data=user_data,
                    stream=False
                )
                
                if response:
                    # Dynamic retrieval of columns
                    desc = response.row.get("description", "No description generated")
                    summary = response.row.get("summary", "No summary generated")
                    
                    st.subheader("📋 Situation Description")
                    st.write(desc)
                    st.divider()
                    st.subheader("📢 Action Summary")
                    st.success(summary)
            except Exception as e:
                st.error(f"An error occurred: {e}")

# ==========================================
# TAB 2: MULTI INPUT ACTION TABLE
# ==========================================
with tab2:
    st.header("Multi-Modality Fusion")
    st.info(f"Connected to Table: `{TABLE_ID_MULTI}`")
    
    col1, col2 = st.columns(2)
    
    with col1:
        multi_text = st.text_area("Text Input", height=150)
        multi_audio = st.file_uploader("Audio Input", type=["mp3", "wav"], key="m_audio")
    
    with col2:
        multi_photo = st.file_uploader("Photo Input", type=["jpg", "png"], key="m_photo")
        if multi_photo:
            st.image(multi_photo, width=200)

    if st.button("Analyze Combined Data"):
        if not (multi_text or multi_audio or multi_photo):
            st.error("Please provide at least one input.")
        else:
            with st.spinner("Processing multi-modal emergency data..."):
                try:
                    multi_data = {}
                    
                    if multi_text:
                        multi_data["text"] = multi_text
                    
                    if multi_audio:
                        p_audio = save_uploaded_file(multi_audio)
                        uri_audio = jamai.file.upload_file(p_audio).uri
                        multi_data["audio"] = uri_audio
                        
                    if multi_photo:
                        p_photo = save_uploaded_file(multi_photo)
                        uri_photo = jamai.file.upload_file(p_photo).uri
                        multi_data["photo"] = uri_photo

                    # Send to Jamai
                    response = jamai.table.add_row(
                        table_id=TABLE_ID_MULTI,
                        data=multi_data,
                        stream=False
                    )

                    if response:
                        desc = response.row.get("description", "No description generated")
                        summary = response.row.get("summary", "No summary generated")
                        
                        st.subheader("📋 Integrated Description")
                        st.write(desc)
                        st.divider()
                        st.subheader("📢 Strategic Summary")
                        st.success(summary)

                except Exception as e:
                    st.error(f"An error occurred during fusion: {e}")