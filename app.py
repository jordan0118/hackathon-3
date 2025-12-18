import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px
from functools import lru_cache

# Configure Streamlit page
st.set_page_config(
    page_title="Emergency Response System",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .emergency-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .alert-high {
        background: #fee;
        border-left: 4px solid #f44336;
    }
    .alert-medium {
        background: #fef3cd;
        border-left: 4px solid #ffc107;
    }
    .alert-low {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== JamAI Integration ====================
class JamAIIntegration:
    """Handles all JamAI API interactions"""
    
    def __init__(self):
        self.api_key = st.secrets.get("jamai_api_key", "demo_key")
        self.base_url = "https://api.jamai.io/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @lru_cache(maxsize=128)
    def analyze_emergency(self, emergency_type: str, description: str) -> Dict:
        """Analyze emergency using JamAI"""
        try:
            payload = {
                "emergency_type": emergency_type,
                "description": description,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # In production, replace with actual JamAI API call
            response = self._mock_analyze(emergency_type, description)
            return response
        except Exception as e:
            st.error(f"Error analyzing emergency: {str(e)}")
            return self._mock_analyze(emergency_type, description)
    
    def _mock_analyze(self, emergency_type: str, description: str) -> Dict:
        """Mock analysis for demonstration"""
        severity_map = {
            "medical": {"severity": 8, "priority": "HIGH"},
            "fire": {"severity": 9, "priority": "CRITICAL"},
            "accident": {"severity": 7, "priority": "HIGH"},
            "weather": {"severity": 6, "priority": "MEDIUM"},
            "other": {"severity": 5, "priority": "MEDIUM"}
        }
        
        analysis = severity_map.get(emergency_type.lower(), severity_map["other"])
        analysis.update({
            "emergency_type": emergency_type,
            "description": description,
            "recommended_services": self._get_recommended_services(emergency_type),
            "estimated_response_time": f"{np.random.randint(5, 20)} minutes",
            "risk_factors": self._extract_risk_factors(description),
            "ai_confidence": f"{np.random.randint(75, 99)}%"
        })
        return analysis
    
    def _get_recommended_services(self, emergency_type: str) -> List[str]:
        """Get recommended emergency services"""
        services_map = {
            "medical": ["Ambulance", "EMT", "Hospital Coordination"],
            "fire": ["Fire Department", "Hazmat Team", "Evacuation Support"],
            "accident": ["Police", "Ambulance", "Traffic Control"],
            "weather": ["Weather Service", "Emergency Management", "Public Alert"],
            "other": ["Police", "Paramedics", "Fire Department"]
        }
        return services_map.get(emergency_type.lower(), services_map["other"])
    
    def _extract_risk_factors(self, description: str) -> List[str]:
        """Extract risk factors from description"""
        risk_keywords = {
            "unconscious": "Loss of consciousness",
            "bleeding": "Severe bleeding",
            "fire": "Active fire hazard",
            "smoke": "Smoke inhalation risk",
            "trapped": "People potentially trapped",
            "hazardous": "Hazardous materials present"
        }
        
        risks = []
        for keyword, risk in risk_keywords.items():
            if keyword.lower() in description.lower():
                risks.append(risk)
        return risks if risks else ["Initial assessment required"]
    
    def predict_resources(self, incident_data: Dict) -> Dict:
        """Predict required resources using AI"""
        return {
            "ambulances": np.random.randint(1, 4),
            "fire_trucks": np.random.randint(0, 3),
            "police_units": np.random.randint(1, 3),
            "personnel": np.random.randint(5, 20),
            "estimated_cost": f"${np.random.randint(1000, 50000)}"
        }

# ==================== Session State Initialization ====================
if 'jamai' not in st.session_state:
    st.session_state.jamai = JamAIIntegration()

if 'emergency_reports' not in st.session_state:
    st.session_state.emergency_reports = []

if 'active_incidents' not in st.session_state:
    st.session_state.active_incidents = []

# ==================== Utility Functions ====================
def get_severity_color(severity: int) -> str:
    """Get color based on severity level"""
    if severity >= 8:
        return "🔴"
    elif severity >= 6:
        return "🟠"
    else:
        return "🟡"

def get_priority_badge(priority: str) -> str:
    """Get HTML badge for priority"""
    colors = {
        "CRITICAL": "#f44336",
        "HIGH": "#ff9800",
        "MEDIUM": "#ffc107",
        "LOW": "#4caf50"
    }
    color = colors.get(priority, "#9e9e9e")
    return f'<span style="background:{color};color:white;padding:5px 10px;border-radius:5px;font-weight:bold">{priority}</span>'

def create_incident_report(incident_data: Dict) -> Dict:
    """Create a structured incident report"""
    report = {
        "id": f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now(),
        "type": incident_data.get("type", "Unknown"),
        "location": incident_data.get("location", "TBD"),
        "description": incident_data.get("description", ""),
        "reporter": incident_data.get("reporter", "Anonymous"),
        "phone": incident_data.get("phone", "N/A"),
        "status": "PENDING",
        "analysis": st.session_state.jamai.analyze_emergency(
            incident_data.get("type", "other"),
            incident_data.get("description", "")
        )
    }
    return report

# ==================== Main Application ====================
def main():
    # Header
    st.markdown("""
    <div class="emergency-banner">
        <h1>🚨 Emergency Response Management System</h1>
        <p>AI-Powered Emergency Dispatch & Resource Allocation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main navigation
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Report Emergency",
        "📊 Active Incidents",
        "📈 Analytics Dashboard",
        "🗺️ Incident Map",
        "⚙️ Resource Management",
        "🤖 AI Assistant"
    ])
    
    # ==================== Tab 1: Report Emergency ====================
    with tab1:
        st.header("Report an Emergency")
        
        col1, col2 = st.columns(2)
        
        with col1:
            emergency_type = st.selectbox(
                "Emergency Type",
                ["Medical", "Fire", "Accident", "Weather", "Other"]
            )
            
            location = st.text_input(
                "Location",
                placeholder="Enter address or location details"
            )
            
            reporter_name = st.text_input(
                "Your Name",
                placeholder="Who is reporting this?"
            )
        
        with col2:
            severity = st.slider(
                "Initial Severity Assessment",
                1, 10, 5,
                help="1 = Minor, 10 = Life-threatening"
            )
            
            phone = st.text_input(
                "Contact Phone",
                placeholder="Your phone number"
            )
            
            reporter_location = st.radio(
                "Are you at the incident location?",
                ["Yes", "No", "Nearby"]
            )
        
        # Description
        description = st.text_area(
            "Incident Description",
            placeholder="Provide detailed information about the emergency...",
            height=150
        )
        
        # Additional details
        st.subheader("Additional Information")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            num_people = st.number_input(
                "Number of People Involved",
                min_value=0,
                max_value=100,
                value=1
            )
        
        with col4:
            injuries = st.multiselect(
                "Injuries (if applicable)",
                ["Minor", "Moderate", "Severe", "Unknown"]
            )
        
        with col5:
            hazards = st.multiselect(
                "Potential Hazards",
                ["Fire", "Chemicals", "Gas", "Electrical", "Other"]
            )
        
        # Submit button
        if st.button("🚨 SUBMIT EMERGENCY REPORT", use_container_width=True, type="primary"):
            incident_data = {
                "type": emergency_type,
                "location": location,
                "description": description,
                "reporter": reporter_name,
                "phone": phone,
                "severity": severity,
                "num_people": num_people,
                "injuries": injuries,
                "hazards": hazards
            }
            
            # Create report
            report = create_incident_report(incident_data)
            st.session_state.emergency_reports.append(report)
            
            # Display confirmation
            st.success("✅ Emergency Report Submitted Successfully!")
            
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                st.metric("Incident ID", report["id"])
            
            with col_info2:
                st.metric("Severity", f"{report['analysis']['severity']}/10")
            
            with col_info3:
                st.metric("Priority", report['analysis']['priority'])
            
            st.markdown("---")
            
            # Analysis results
            st.subheader("AI Analysis Results")
            
            analysis = report['analysis']
            
            col_a1, col_a2 = st.columns(2)
            
            with col_a1:
                st.write("**Recommended Services:**")
                for service in analysis['recommended_services']:
                    st.write(f"✓ {service}")
            
            with col_a2:
                st.write("**Risk Factors:**")
                for risk in analysis['risk_factors']:
                    st.write(f"⚠️ {risk}")
            
            st.write(f"**Estimated Response Time:** {analysis['estimated_response_time']}")
            st.write(f"**AI Confidence:** {analysis['ai_confidence']}")
    
    # ==================== Tab 2: Active Incidents ====================
    with tab2:
        st.header("Active Incidents")
        
        if st.session_state.emergency_reports:
            # Filter options
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                filter_type = st.multiselect(
                    "Filter by Type",
                    ["Medical", "Fire", "Accident", "Weather", "Other"],
                    default=["Medical", "Fire", "Accident"]
                )
            
            with col_f2:
                filter_priority = st.multiselect(
                    "Filter by Priority",
                    ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                    default=["CRITICAL", "HIGH"]
                )
            
            with col_f3:
                filter_status = st.multiselect(
                    "Filter by Status",
                    ["PENDING", "RESPONDING", "ON_SCENE", "RESOLVED"],
                    default=["PENDING", "RESPONDING"]
                )
            
            st.markdown("---")
            
            # Display incidents
            for idx, report in enumerate(reversed(st.session_state.emergency_reports)):
                if (report['type'] in filter_type and 
                    report['analysis']['priority'] in filter_priority and
                    report['status'] in filter_status):
                    
                    with st.container():
                        col_inc1, col_inc2, col_inc3, col_inc4 = st.columns([2, 2, 2, 1])
                        
                        with col_inc1:
                            st.write(f"**{report['id']}**")
                            st.caption(f"📍 {report['location']}")
                        
                        with col_inc2:
                            severity_icon = get_severity_color(report['analysis']['severity'])
                            st.write(f"{severity_icon} Type: {report['type']}")
                            st.markdown(get_priority_badge(report['analysis']['priority']), unsafe_allow_html=True)
                        
                        with col_inc3:
                            st.write(f"Reporter: {report['reporter']}")
                            st.caption(f"Time: {report['timestamp'].strftime('%H:%M:%S')}")
                        
                        with col_inc4:
                            status_color = {
                                "PENDING": "🟡",
                                "RESPONDING": "🟠",
                                "ON_SCENE": "🔵",
                                "RESOLVED": "🟢"
                            }
                            st.write(status_color.get(report['status'], "❓"))
                        
                        # Expandable details
                        with st.expander(f"📋 Details - {report['id']}"):
                            st.write(f"**Description:** {report['description']}")
                            st.write(f"**Contact:** {report['phone']}")
                            
                            col_det1, col_det2 = st.columns(2)
                            
                            with col_det1:
                                st.write("**Recommended Services:**")
                                for service in report['analysis']['recommended_services']:
                                    st.write(f"• {service}")
                            
                            with col_det2:
                                st.write("**Risk Factors:**")
                                for risk in report['analysis']['risk_factors']:
                                    st.write(f"• {risk}")
                            
                            # Resource prediction
                            resources = st.session_state.jamai.predict_resources(report)
                            st.write("**Predicted Resource Requirement:**")
                            res_col1, res_col2, res_col3, res_col4 = st.columns(4)
                            with res_col1:
                                st.metric("Ambulances", resources['ambulances'])
                            with res_col2:
                                st.metric("Fire Trucks", resources['fire_trucks'])
                            with res_col3:
                                st.metric("Police Units", resources['police_units'])
                            with res_col4:
                                st.metric("Est. Cost", resources['estimated_cost'])
                        
                        st.markdown("---")
        else:
            st.info("ℹ️ No emergency reports yet. Create one to get started.")
    
    # ==================== Tab 3: Analytics Dashboard ====================
    with tab3:
        st.header("Analytics Dashboard")
        
        if st.session_state.emergency_reports:
            # Summary metrics
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            total_incidents = len(st.session_state.emergency_reports)
            critical_count = sum(1 for r in st.session_state.emergency_reports 
                               if r['analysis']['severity'] >= 8)
            avg_severity = np.mean([r['analysis']['severity'] 
                                   for r in st.session_state.emergency_reports])
            
            with col_m1:
                st.metric("Total Incidents", total_incidents)
            with col_m2:
                st.metric("Critical Cases", critical_count)
            with col_m3:
                st.metric("Avg Severity", f"{avg_severity:.1f}/10")
            with col_m4:
                st.metric("Response Rate", "94.5%")
            
            st.markdown("---")
            
            # Charts
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Incidents by type
                incident_types = [r['type'] for r in st.session_state.emergency_reports]
                type_counts = pd.Series(incident_types).value_counts()
                
                fig = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    title="Incidents by Type",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col_chart2:
                # Severity distribution
                severities = [r['analysis']['severity'] for r in st.session_state.emergency_reports]
                
                fig = go.Figure(data=[go.Histogram(x=severities, nbinsx=10)])
                fig.update_layout(
                    title="Severity Distribution",
                    xaxis_title="Severity Level",
                    yaxis_title="Number of Incidents",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Timeline
            st.subheader("Incident Timeline")
            
            timeline_data = pd.DataFrame([
                {
                    "Time": r['timestamp'],
                    "Type": r['type'],
                    "Severity": r['analysis']['severity'],
                    "Priority": r['analysis']['priority']
                }
                for r in st.session_state.emergency_reports
            ])
            
            fig = px.scatter(
                timeline_data,
                x="Time",
                y="Severity",
                color="Priority",
                size="Severity",
                hover_data=["Type"],
                title="Incidents Over Time",
                color_discrete_map={
                    "CRITICAL": "#f44336",
                    "HIGH": "#ff9800",
                    "MEDIUM": "#ffc107",
                    "LOW": "#4caf50"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("ℹ️ No data available for analytics yet.")
    
    # ==================== Tab 4: Incident Map ====================
    with tab4:
        st.header("Incident Map")
        
        if st.session_state.emergency_reports:
            # Create mock coordinates for incidents
            map_data = pd.DataFrame([
                {
                    "latitude": 40.7128 + np.random.uniform(-0.1, 0.1),
                    "longitude": -74.0060 + np.random.uniform(-0.1, 0.1),
                    "type": r['type'],
                    "severity": r['analysis']['severity'],
                    "location": r['location']
                }
                for r in st.session_state.emergency_reports
            ])
            
            st.map(map_data, zoom=10)
            
            # Location statistics
            st.subheader("Location Statistics")
            location_counts = pd.Series([r['location'] for r in st.session_state.emergency_reports]).value_counts()
            
            fig = px.bar(
                x=location_counts.index,
                y=location_counts.values,
                title="Incidents by Location",
                labels={"x": "Location", "y": "Count"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ No incidents to display on map.")
    
    # ==================== Tab 5: Resource Management ====================
    with tab5:
        st.header("Resource Management")
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.subheader("Available Resources")
            
            resources = {
                "Ambulances": {"available": 15, "deployed": 3},
                "Fire Trucks": {"available": 8, "deployed": 2},
                "Police Units": {"available": 25, "deployed": 7},
                "Helicopters": {"available": 2, "deployed": 0},
                "Paramedics": {"available": 45, "deployed": 12}
            }
            
            for resource, data in resources.items():
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    st.metric(resource, data['available'])
                with col_r2:
                    st.caption(f"Deployed: {data['deployed']}")
                with col_r3:
                    utilization = (data['deployed'] / (data['available'] + data['deployed'])) * 100
                    st.caption(f"{utilization:.1f}% utilized")
        
        with col_res2:
            st.subheader("Resource Allocation by Incident")
            
            if st.session_state.emergency_reports:
                allocation_data = []
                for idx, report in enumerate(st.session_state.emergency_reports[:5], 1):
                    resources_pred = st.session_state.jamai.predict_resources(report)
                    allocation_data.append({
                        "Incident": report['id'],
                        "Ambulances": resources_pred['ambulances'],
                        "Fire Trucks": resources_pred['fire_trucks'],
                        "Police Units": resources_pred['police_units']
                    })
                
                allocation_df = pd.DataFrame(allocation_data)
                st.bar_chart(allocation_df.set_index("Incident"))
            else:
                st.info("ℹ️ No incidents for resource allocation.")
    
    # ==================== Tab 6: AI Assistant ====================
    with tab6:
        st.header("🤖 Emergency Response AI Assistant")
        
        st.write("""
        This AI assistant uses JamAI integration to provide intelligent emergency response recommendations.
        """)
        
        col_ai1, col_ai2 = st.columns([2, 1])
        
        with col_ai1:
            ai_query = st.text_area(
                "Ask the AI Assistant",
                placeholder="e.g., 'What resources are needed for a major fire incident?' or 'Predict dispatch time for medical emergency'",
                height=100
            )
        
        with col_ai2:
            query_category = st.selectbox(
                "Query Category",
                ["Resource Prediction", "Incident Analysis", "Best Practices", "Optimization"]
            )
        
        if st.button("🤖 Get AI Recommendation", use_container_width=True, type="primary"):
            if ai_query:
                with st.spinner("Processing with JamAI..."):
                    # Simulate AI response
                    responses = {
                        "Resource Prediction": "Based on current incident patterns, major fire incidents typically require: 3-4 fire trucks, 2 ambulances, 1 helicopter, and 15-20 personnel. Response time averages 8-12 minutes.",
                        "Incident Analysis": "The incident shows moderate to high risk factors. Recommended immediate actions: establish perimeter, evacuate surrounding areas, and coordinate with utility companies if applicable.",
                        "Best Practices": "For optimal emergency response: 1) Ensure real-time communication channels, 2) Pre-position resources strategically, 3) Conduct regular drills, 4) Implement AI-driven dispatch, 5) Monitor response metrics.",
                        "Optimization": "Current system can improve dispatch time by 15-20% through predictive positioning and ML-based resource allocation. Recommend implementing real-time traffic routing."
                    }
                    
                    response = responses.get(query_category, "Response generated by JamAI")
                
                st.success("✅ AI Analysis Complete")
                
                with st.container():
                    st.markdown(f"""
                    **Query:** {ai_query}
                    
                    **Category:** {query_category}
                    
                    **AI Response:**
                    
                    {response}
                    
                    **Confidence:** 92% | **Processing Time:** 234ms
                    """)
        
        st.markdown("---")
        
        st.subheader("Quick AI Insights")
        
        col_ai_i1, col_ai_i2, col_ai_i3 = st.columns(3)
        
        with col_ai_i1:
            st.info("""
            **🎯 Peak Hours Analysis**
            
            Most incidents occur between 4-6 PM. 
            Recommend additional resources during this window.
            """)
        
        with col_ai_i2:
            st.warning("""
            **⚠️ Resource Alert**
            
            Paramedic availability down to 60%.
            Consider requesting mutual aid.
            """)
        
        with col_ai_i3:
            st.success("""
            **✅ Performance Metric**
            
            Average response time improved 8% 
            using AI dispatch optimization.
            """)

if __name__ == "__main__":
    main()
