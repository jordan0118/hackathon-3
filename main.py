import streamlit as st
import time
import random

# --- 1. Basic Page Configuration (Must be the first command) ---
st.set_page_config(
    page_title="AERN - AI Emergency Response",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Custom Styling (Decorations & CSS) ---
# Used to make buttons larger and style the chat bubbles for a better UX
st.markdown("""
<style>
    /* Emergency button style */
    .stButton>button {
        height: 3em;
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        font-size: 20px;
    }
    /* Chat bubble style */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Top Configuration Area (Your request: Top 3 Rows for JamAI) ---
with st.expander("🛠 Developer Configuration (JamAI Base Setup)", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        jamai_api_key = st.text_input("1. JamAI API Key", type="password", placeholder="sk-...")
    with col2:
        project_id = st.text_input("2. Project ID", placeholder="proj_...")
    with col3:
        table_id = st.text_input("3. Knowledge Table ID", placeholder="gen_table_...")

    # Simple connection status check
    if jamai_api_key and project_id:
        st.success("✅ JamAI Configuration Loaded (Ready to connect)")
    else:
        st.info("ℹ️ Running in Simulation Mode (No API Key detected)")

st.divider() # Divider

# --- 4. State Management (Session State) ---
# Used to remember chat history and check if "panic mode" is active
if "messages" not in st.session_state:
    st.session_state.messages = []
if "panic_mode" not in st.session_state:
    st.session_state.panic_mode = False

# --- 5. Sidebar (Map & Location) ---
with st.sidebar:
    st.header("📍 Current Status")
    st.write("Location: Kamunting, Perak")
    st.write("Risk Level: 🟡 Moderate")
    
    # Simulated Map (Google Static Maps placeholder)
    st.image("https://maps.googleapis.com/maps/api/staticmap?center=Kamunting&zoom=13&size=400x400&maptype=roadmap&markers=color:red%7Clabel:S%7CKamunting", caption="Nearby Safe Zones")
    
    st.markdown("### 📞 Emergency Contacts")
    st.info("🚑 Hospital: 999\n\n🚒 Fire: 994\n\n👮 Police: 999")

# --- 6. Main Interface Logic ---

# Title
st.title("🚨 AERN: Emergency Response Navigator")

# Define two tabs: Panic Mode and AI Assistant
tab1, tab2 = st.tabs(["🔥 PANIC MODE (SOS)", "💬 AI Chat Assistant"])

# === TAB 1: Panic Mode ===
with tab1:
    st.markdown("### Select Emergency Type")
    
    # Three massive emergency buttons
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        if st.button("🌊 FLOOD"):
            st.session_state.messages.append({"role": "user", "content": "HELP! It's flooding and water is rising fast!"})
            st.session_state.panic_trigger = "flood"
            st.toast("🚨 Switching to Emergency Protocol: FLOOD")
            
    with col_p2:
        if st.button("🔥 FIRE"):
            st.session_state.messages.append({"role": "user", "content": "HELP! There is a fire in the building!"})
            st.session_state.panic_trigger = "fire"
            st.toast("🚨 Switching to Emergency Protocol: FIRE")
            
    with col_p3:
        if st.button("🚑 MEDICAL"):
            st.session_state.messages.append({"role": "user", "content": "HELP! Someone is unconscious!"})
            st.session_state.panic_trigger = "medical"
            st.toast("🚨 Switching to Emergency Protocol: MEDICAL")

    # If button clicked, show emergency card
    if "panic_trigger" in st.session_state:
        st.error(f"⚠️ EMERGENCY DETECTED: {st.session_state.panic_trigger.upper()}")
        st.markdown("""
        Action Plan:
        1. ✅ Stay Calm
        2. 🚫 Do NOT use elevators
        3. 🏃 Move to open ground
        4. 📍 Map Updated: Nearest shelter is 1.2km away.
        """)
        # === TAB 2: AI Chat Assistant ===
with tab2:
    st.write("Describe your situation in detail. AI allows Manglish.")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input box
    if prompt := st.chat_input("Apa jadi? Type here..."):
        # 1. Display user input
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Simulate AI thinking process
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Analyzing situation... 🧠")
            time.sleep(1.5) # Pretend to think
            
            # --- Future integration point for JamAI (Zixuan's part) ---
            # if jamai_api_key:
            #     response = zixuan_function(prompt, jamai_api_key)
            # else:
            #     response = "Simulated response..."
            # ---------------------------------------------------------
            
            # Current simulated response
            full_response = f"I have received your report: '{prompt}'. \n\nBased on your location (Kamunting), here is the advice:\n1. Ensure your safety first.\n2. If water level is rising, turn off main power.\n3. Contacting 999..."
            
            message_placeholder.markdown(full_response)
        
        # Save AI response
        st.session_state.messages.append({"role": "assistant", "content": full_response})