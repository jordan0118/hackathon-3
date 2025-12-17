import streamlit as st
import tempfile
import os
import sys
import time
from jamaibase import JamAI, protocol as p  # keep teammate's import (protocol unused but preserved)

# -----------------------
# Page / UI configuration
# -----------------------
st.set_page_config(page_title="AERN | AI Emergency Response Navigator", page_icon="🚨", layout="wide")

st.markdown("""
<style>
    .stButton>button {height: 3em; width: 100%; border-radius: 10px; font-weight: bold; font-size: 20px;} 
    .stChatMessage {border-radius: 15px; padding: 10px;}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Secrets / Credentials
# -----------------------
# Support both naming schemes:
# - New teammate scheme: st.secrets["JAMAI_API_KEY"], st.secrets["PROJECT_ID"], st.secrets["TABLE_ID"]
# - Existing scheme: JAMAI_PROJECT_ID / JAMAI_PAT_KEY or environment variables JAMAI_PROJECT_ID / JAMAI_PAT_KEY
def _load_secrets():
    # prefer streamlit secrets when present
    proj = None
    pat = None
    table_text = None
    table_audio = None
    table_photo = None
    table_multi = None
    table_chat = None

    if hasattr(st, "secrets") and isinstance(st.secrets, dict) and st.secrets:
        # teammate keys
        pat = st.secrets.get("JAMAI_API_KEY") or st.secrets.get("JAMAI_PAT_KEY")
        proj = st.secrets.get("PROJECT_ID") or st.secrets.get("JAMAI_PROJECT_ID")
        # optional per-table ids
        table_text = st.secrets.get("TABLE_TEXT_ID") or st.secrets.get("TABLE_ID_TEXT") or st.secrets.get("TABLE_ID")
        table_audio = st.secrets.get("TABLE_AUDIO_ID") or st.secrets.get("TABLE_ID_AUDIO")
        table_photo = st.secrets.get("TABLE_PHOTO_ID") or st.secrets.get("TABLE_ID_PHOTO")
        table_multi = st.secrets.get("TABLE_MULTI_ID") or st.secrets.get("TABLE_ID_MULTI")
        table_chat = st.secrets.get("TABLE_CHAT_ID") or st.secrets.get("TABLE_ID_CHAT") or st.secrets.get("TABLE_ID")
    # fallback to environment
    if not proj:
        proj = os.getenv("JAMAI_PROJECT_ID") or os.getenv("PROJECT_ID")
    if not pat:
        pat = os.getenv("JAMAI_PAT_KEY") or os.getenv("JAMAI_API_KEY") or os.getenv("JAMAI_PAT")
    # fallback table ids (hard-coded defaults; update to your actual table IDs)
    table_text = table_text or os.getenv("TABLE_ID_TEXT") or "text_received"
    table_audio = table_audio or os.getenv("TABLE_ID_AUDIO") or "audio_receive"
    table_photo = table_photo or os.getenv("TABLE_ID_PHOTO") or "picture_receipt"
    table_multi = table_multi or os.getenv("TABLE_ID_MULTI") or "combined"
    table_chat = table_chat or os.getenv("TABLE_ID_CHAT") or table_multi

    return proj.strip() if isinstance(proj, str) else proj, (pat.strip() if isinstance(pat, str) else pat), {
        "text": table_text, "audio": table_audio, "photo": table_photo, "multi": table_multi, "chat": table_chat
    }

PROJECT_ID, PAT_KEY, TABLE_IDS = _load_secrets()

# show connection status
if PROJECT_ID and PAT_KEY:
    st.sidebar.success("✅ JamAI credentials loaded")
else:
    st.sidebar.warning("⚠️ JamAI credentials missing. Set secrets or environment variables.")

# -----------------------
# Initialize JamAI client
# -----------------------
jamai = None
if PROJECT_ID and PAT_KEY:
    try:
        jamai = JamAI(token=PAT_KEY, project_id=PROJECT_ID)
    except Exception as e:
        st.sidebar.error(f"Failed to initialize JamAI client: {e}")
        jamai = None

# -----------------------
# Helpers (file save, upload, send)
# -----------------------
def save_uploaded_file(uploaded_file):
    try:
        suffix = f".{uploaded_file.name.split('.')[-1]}" if "." in uploaded_file.name else ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving uploaded file: {e}")
        return None

def _get_uri_from_upload(upload_resp):
    if upload_resp is None:
        return None
    if isinstance(upload_resp, dict):
        return upload_resp.get("uri") or upload_resp.get("url")
    if hasattr(upload_resp, "uri"):
        return getattr(upload_resp, "uri", None)
    if hasattr(upload_resp, "url"):
        return getattr(upload_resp, "url", None)
    if hasattr(upload_resp, "row") and isinstance(upload_resp.row, dict):
        return upload_resp.row.get("uri") or upload_resp.row.get("url")
    return None

def _normalize_row_dict(d):
    if not isinstance(d, dict):
        return {}
    for key in ("values", "fields", "data"):
        if key in d and isinstance(d[key], dict):
            return d[key]
    return d

def _find_row_dict(response):
    if response is None:
        return {}
    if isinstance(response, list) and response:
        candidate = response[0]
        if isinstance(candidate, dict):
            return _normalize_row_dict(candidate)
    if isinstance(response, dict):
        if "row" in response and isinstance(response["row"], dict):
            return _normalize_row_dict(response["row"])
        if "rows" in response and isinstance(response["rows"], list) and response["rows"]:
            return _normalize_row_dict(response["rows"][0])
        if "values" in response and isinstance(response["values"], dict):
            return _normalize_row_dict(response["values"])
        if "data" in response and isinstance(response["data"], dict):
            return _normalize_row_dict(response["data"])
        return _normalize_row_dict(response)
    if hasattr(response, "row"):
        try:
            r = getattr(response, "row")
            if isinstance(r, dict):
                return _normalize_row_dict(r)
        except Exception:
            pass
    if hasattr(response, "rows"):
        try:
            rlist = getattr(response, "rows")
            if isinstance(rlist, list) and rlist:
                return _normalize_row_dict(rlist[0])
        except Exception:
            pass
    if hasattr(response, "__dict__"):
        d = getattr(response, "__dict__", {})
        return _find_row_dict(d)
    return {}

def _extract_field_safe(row_dict, key, default=None):
    if not isinstance(row_dict, dict):
        return default
    if key in row_dict:
        return row_dict.get(key)
    # search nested
    def search(obj):
        if isinstance(obj, dict):
            if key in obj:
                return obj[key]
            for v in obj.values():
                res = search(v)
                if res is not None:
                    return res
        if isinstance(obj, list):
            for item in obj:
                res = search(item)
                if res is not None:
                    return res
        return None
    found = search(row_dict)
    return found if found is not None else default

def _cleanup_temp(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

def send_table_row(table_id, data, stream=False):
    """
    Insert a row using JamAI's table methods.
    """
    if jamai is None:
        raise RuntimeError("JamAI client not initialized.")
    table_obj = getattr(jamai, "table", None)
    if table_obj is None:
        raise AttributeError("jamai.table is not present on the JamAI client instance.")

    # Use the add_table_rows method if available
    if hasattr(table_obj, "add_table_rows") and callable(getattr(table_obj, "add_table_rows")):
        try:
            return table_obj.add_table_rows(table_id=table_id, rows=[data])  # Correctly pass rows as a single argument
        except AttributeError as e:
            raise RuntimeError(f"jamai.table.add_table_rows raised an error: {e}") from e

    # Fallback to add_table_row if add_table_rows is not available
    if hasattr(table_obj, "add_table_row") and callable(getattr(table_obj, "add_table_row")):
        try:
            return table_obj.add_table_row(table_id=table_id, row=data)
        except Exception as e:
            raise RuntimeError(f"jamai.table.add_table_row raised an error: {e}") from e

    raise AttributeError("Could not find an API to insert rows on jamai.table.")

# -----------------------
# Main AI Assistant Tab changes
# -----------------------
st.header("💬 AI Assistant Improved")
# Note: Improve assistive behavior based! 
