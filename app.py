import streamlit as st
import anthropic
import json
from datetime import datetime

# Initialize Anthropic client
client = anthropic.Anthropic()

# Page configuration
st.set_page_config(page_title="Emergency Response & Self-Care AI", layout="wide")

# Custom CSS for better UI
st.markdown("""
    <style>
    .emergency-box {
        background-color: #fff3cd;
        border-left: 4px solid #ff6b6b;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .guidance-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .self-care-box {
        background-color: #e7f3ff;
        border-left: 4px solid #0066cc;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def get_emergency_guidance(emergency_type: str) -> str:
    """Get AI-powered guidance for emergency situations"""
    
    prompt = f"""You are an emergency response AI assistant. A person is experiencing a {emergency_type} emergency.
    
Provide immediate, practical guidance for handling this emergency. Include:
1. Immediate steps to take (first 5 minutes)
2. Safety considerations
3. When and how to contact professional help
4. Important precautions to avoid making the situation worse

Keep the response concise, actionable, and calm in tone. Format with clear sections."""
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text

def get_self_care_recommendations(concern: str) -> str:
    """Get personalized self-care recommendations"""
    
    prompt = f"""You are a compassionate wellness coach. Someone is dealing with: {concern}
    
Provide 5-7 practical self-care recommendations that include:
- Mental/emotional practices
- Physical wellness activities
- Social/connection strategies
- Professional resources if needed

Make recommendations specific, actionable, and encouraging. Keep the tone supportive."""
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text

def main():
    st.title("🆘 Emergency Response & 💝 Self-Care AI Assistant")
    
    # Sidebar for navigation
    page = st.sidebar.radio("Choose a service:", 
                           ["Emergency Response", "Self-Care Support"])
    
    if page == "Emergency Response":
        st.header("🆘 Emergency Response Guidance")
        st.markdown("Select your emergency type to receive immediate AI guidance.")
        
        # Emergency types with immediate processing
        emergency_types = [
            "Medical Emergency (chest pain, severe bleeding, etc.)",
            "Mental Health Crisis (severe anxiety, suicidal thoughts)",
            "Fire or Smoke",
            "Vehicle Accident",
            "Poisoning or Overdose",
            "Severe Allergic Reaction",
            "Active Violence or Threat",
            "Natural Disaster",
            "Carbon Monoxide Exposure",
            "Severe Injury or Trauma"
        ]
        
        # Create columns for emergency type selection
        col1, col2 = st.columns(2)
        
        selected_emergency = None
        
        with col1:
            selected_emergency = st.selectbox(
                "Select Emergency Type:",
                options=emergency_types,
                label_visibility="collapsed"
            )
        
        # Immediately process when selection changes
        if selected_emergency:
            st.markdown('<div class="emergency-box">', unsafe_allow_html=True)
            st.warning(f"⚠️ **Emergency Type:** {selected_emergency}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Show loading state while generating guidance
            with st.spinner("🤖 Generating immediate guidance..."):
                guidance = get_emergency_guidance(selected_emergency)
            
            # Display guidance in a highlighted box
            st.markdown('<div class="guidance-box">', unsafe_allow_html=True)
            st.markdown("### 📋 Immediate Guidance")
            st.markdown(guidance)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Emergency contacts reminder
            st.markdown("---")
            st.info("""
            **📞 Emergency Contacts:**
            - Emergency Services (Life-threatening): **911** (US) or your local emergency number
            - National Suicide Prevention Lifeline: **988** (US)
            - Crisis Text Line: Text **HOME** to **741741**
            """)
            
            # Option to get additional resources
            if st.button("📚 Get Additional Resources"):
                with st.spinner("Loading resources..."):
                    resources_prompt = f"""Provide 3-5 reliable resources, hotlines, and organizations 
                    that specialize in {selected_emergency}. Include website URLs if available."""
                    
                    resources = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=512,
                        messages=[
                            {"role": "user", "content": resources_prompt}
                        ]
                    )
                    
                    st.markdown("### 🔗 Additional Resources")
                    st.markdown(resources.content[0].text)
    
    else:  # Self-Care Support
        st.header("💝 Self-Care Support")
        st.markdown("Describe what you're going through to receive personalized recommendations.")
        
        # Self-care concern input
        concern = st.text_area(
            "What are you dealing with? (Please be specific)",
            placeholder="E.g., 'I've been feeling overwhelmed with work stress and anxiety...'",
            height=100
        )
        
        if st.button("💪 Get Self-Care Recommendations", use_container_width=True):
            if concern.strip():
                with st.spinner("🤖 Creating personalized recommendations..."):
                    recommendations = get_self_care_recommendations(concern)
                
                st.markdown('<div class="self-care-box">', unsafe_allow_html=True)
                st.markdown("### 🌟 Personalized Self-Care Plan")
                st.markdown(recommendations)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Tracking option
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ Mark as helpful"):
                        st.success("Thank you for your feedback!")
                with col2:
                    if st.button("💾 Save recommendations"):
                        st.info("Recommendations saved to your session!")
                with col3:
                    if st.button("🔄 Get different suggestions"):
                        st.session_state['regenerate'] = True
                        st.rerun()
            else:
                st.warning("Please describe what you're going through to receive personalized recommendations.")

if __name__ == "__main__":
    main()
