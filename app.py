import streamlit as st
import tempfile
import os
from jamaibase import JamAI

# --- CONFIGURATION ---
# Read credentials from environment variables (do NOT commit secrets)
PROJECT_ID = os.getenv("proj_cbb373ee0918dc48e8a09c69", "").strip()
PAT_KEY = os.getenv("jamai_pat_adf3eaec83074e0cd99cfa0d7a2d2ecdf97107f3705bf306", "").strip()

# --- ACTION TABLE IDS ---
# Replace these with your actual table IDs (avoid percent-encoding if possible)
TABLE_ID_TEXT = "text%20received"
TABLE_ID_AUDIO = "audio_receive"
TABLE_ID_PHOTO = "picture%20receipt"
TABLE_ID_MULTI = "combined"

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AERN | AI Emergency Response Navigator",
    page_icon="🚨",
    layout="centered"
)

# --- VERIFY CREDENTIALS ---
if not PROJECT_ID or not PAT_KEY:
    st.error("🚨 Set JAMAI_PROJECT_ID and JAMAI_PAT_KEY in environment or in Streamlit secrets.")
    st.stop()

# --- INITIALIZE JAMAI CLIENT ---
try:
    jamai = JamAI(token=PAT_KEY, project_id=PROJECT_ID)
except Exception as e:
    st.error(f"Failed to initialize JamAI client: {e}")
    st.stop()

# --- HELPER FUNCTION: SAVE UPLOADED FILE ---
def save_uploaded_file(uploaded_file):
    """
    Save a Streamlit uploaded file to a temp path so the JamAI SDK can read it.
    Returns the temp path or None on error.
    """
    try:
        suffix = f".{uploaded_file.name.split('.')[-1]}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error handling file: {e}")
        return None

def _extract_row(response):
    """
    Safely extract a row dict from the SDK response object.
    """
    if response is None:
        return {}
    # If SDK returns a dict-like response
    if isinstance(response, dict):
        return response.get("row", {}) or {}
    # If SDK returns an object with attribute 'row'
    if hasattr(response, "row"):
        try:
            r = response.row
            return r or {}
        except Exception:
            return {}
    # Fallback: try __dict__
    if hasattr(response, "__dict__"):
        return getattr(response, "__dict__", {}).get("row", {}) or {}
    return {}

# --- MAIN APP UI ---
st.title("🚨 AERN")
st.caption("AI Emergency Response Navigator")

# --- TABS FOR DIFFERENT MODES ---
tab1, tab2 = st.tabs(["Single Modality Analysis", "Multi-Modality Fusion"])

# ==========================================
# TAB 1: THREE SEPARATE SINGLE INPUT ACTION TABLES
# ==========================================
with tab1:
    st.header("Single Input Analysis (3 Dedicated Tables)")
    st.info("Input will be sent to the table matching the input type.")
    
    input_type = st.radio("Select Input Type", ["Text", "Audio", "Photo"], horizontal=True)
    
    user_data = {}
    table_id_to_use = None
    ready_to_send = False

    # --- Input and Routing Logic ---
    if input_type == "Text":
        text_input = st.text_area("Describe the emergency situation:")
        if text_input:
            user_data = {"text": text_input}  # adjust key to match your table column
            table_id_to_use = TABLE_ID_TEXT
            ready_to_send = True

    elif input_type == "Audio":
        audio_file = st.file_uploader("Upload Audio Recording", type=["mp3", "wav", "m4a"])
        if audio_file:
            path = save_uploaded_file(audio_file)
            if path:
                table_id_to_use = TABLE_ID_AUDIO
                with st.spinner("Uploading audio..."):
                    try:
                        uploaded = jamai.file.upload_file(path)
                        uploaded_uri = getattr(uploaded, "uri", None) or (uploaded.get("uri") if isinstance(uploaded, dict) else None)
                        if not uploaded_uri:
                            st.error("Upload did not return a uri.")
                        else:
                            user_data = {"audio": uploaded_uri}
                            ready_to_send = True
                    except Exception as e:
                        st.error(f"Failed to upload audio: {e}")

    elif input_type == "Photo":
        photo_file = st.file_uploader("Upload Scene Photo", type=["jpg", "png", "jpeg"])
        if photo_file:
            path = save_uploaded_file(photo_file)
            st.image(photo_file, caption="Preview", width=300)
            if path:
                table_id_to_use = TABLE_ID_PHOTO
                with st.spinner("Uploading photo..."):
                    try:
                        uploaded = jamai.file.upload_file(path)
                        uploaded_uri = getattr(uploaded, "uri", None) or (uploaded.get("uri") if isinstance(uploaded, dict) else None)
                        if not uploaded_uri:
                            st.error("Upload did not return a uri.")
                        else:
                            user_data = {"photo": uploaded_uri}
                            ready_to_send = True
                    except Exception as e:
                        st.error(f"Failed to upload photo: {e}")

    # --- Execution ---
    if st.button("Analyze Single Input", disabled=not ready_to_send):
        with st.spinner(f"Consulting AERN Brain via table: {table_id_to_use}..."):
            try:
                response = jamai.table.add_row(
                    table_id=table_id_to_use,
                    data=user_data,
                    stream=False
                )
                row = _extract_row(response)
                desc = row.get("description", "No description generated")
                summary = row.get("summary", "No summary generated")
                
                st.subheader("📋 Situation Description")
                st.write(desc)
                st.divider()
                st.subheader("📢 Action Summary")
                st.success(summary)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.write("Ensure the correct Table ID and column names are configured for the selected input type.")

# ==========================================
# TAB 2: MULTI INPUT ACTION TABLE (REMAINS THE SAME)
# ==========================================
with tab2:
    st.header("Multi-Modality Fusion")
    st.info(f"Connected to Table: `{TABLE_ID_MULTI}` (Assumes one table handles all inputs)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        multi_text = st.text_area("Text Input", height=150)
        multi_audio = st.file_uploader("Audio Input", type=["mp3", "wav", "m4a"], key="m_audio")
    
    with col2:
        multi_photo = st.file_uploader("Photo Input", type=["jpg", "png", "jpeg"], key="m_photo")
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
                        if p_audio:
                            uploaded = jamai.file.upload_file(p_audio)
                            uri_audio = getattr(uploaded, "uri", None) or (uploaded.get("uri") if isinstance(uploaded, dict) else None)
                            if uri_audio:
                                multi_data["audio"] = uri_audio
                            else:
                                st.warning("Audio uploaded but no uri returned.")
                        
                    if multi_photo:
                        p_photo = save_uploaded_file(multi_photo)
                        if p_photo:
                            uploaded = jamai.file.upload_file(p_photo)
                            uri_photo = getattr(uploaded, "uri", None) or (uploaded.get("uri") if isinstance(uploaded, dict) else None)
                            if uri_photo:
                                multi_data["photo"] = uri_photo
                            else:
                                st.warning("Photo uploaded but no uri returned.")

                    # Send to Jamai
                    response = jamai.table.add_row(
                        table_id=TABLE_ID_MULTI,
                        data=multi_data,
                        stream=False
                    )
                    row = _extract_row(response)
                    desc = row.get("description", "No description generated")
                    summary = row.get("summary", "No summary generated")
                    
                    st.subheader("📋 Integrated Description")
                    st.write(desc)
                    st.divider()
                    st.subheader("📢 Strategic Summary")
                    st.success(summary)

                except Exception as e:
                    st.error(f"An error occurred during fusion: {e}")