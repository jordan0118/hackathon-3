import os
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Any
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Emergency Response System with JamAI", version="1.0.0")

# JamAI Configuration
JAMAI_BASE_URL = os.getenv("JAMAI_BASE_URL", "https://api.jamai.io")
JAMAI_API_KEY = os.getenv("JAMAI_API_KEY")
JAMAI_WORKSPACE_ID = os.getenv("JAMAI_WORKSPACE_ID")

# Request/Response Models
class EmergencyReport(BaseModel):
    """Emergency report submission model"""
    incident_type: str
    location: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    timestamp: Optional[str] = None
    contact_info: Optional[str] = None
    additional_details: Optional[Dict[str, Any]] = None


class EmergencyResponse(BaseModel):
    """Emergency response model"""
    incident_id: str
    status: str
    recommended_actions: List[str]
    resources_required: List[str]
    estimated_arrival_time: str
    priority_score: int
    ai_analysis: Dict[str, Any]


class JamAIIntegration:
    """JamAI Integration handler for emergency response"""
    
    def __init__(self):
        self.base_url = JAMAI_BASE_URL
        self.api_key = JAMAI_API_KEY
        self.workspace_id = JAMAI_WORKSPACE_ID
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def initialize(self):
        """Initialize JamAI integration"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            response = await self.client.get(
                f"{self.base_url}/workspaces/{self.workspace_id}",
                headers=headers
            )
            if response.status_code == 200:
                print("✓ JamAI Integration initialized successfully")
                return True
            else:
                print(f"⚠ JamAI initialization warning: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ JamAI initialization error: {str(e)}")
            return False
    
    async def analyze_emergency(self, report: EmergencyReport) -> Dict[str, Any]:
        """Analyze emergency report using JamAI"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Analyze this emergency incident and provide response recommendations:
            
Incident Type: {report.incident_type}
Location: {report.location}
Severity: {report.severity}
Description: {report.description}
Contact: {report.contact_info or 'N/A'}
Additional Details: {json.dumps(report.additional_details or {})}

Provide a JSON response with:
1. risk_assessment (0-100 score)
2. immediate_actions (list of recommended actions)
3. required_resources (list of needed resources)
4. estimated_response_time (in minutes)
5. alternative_locations (nearby emergency services)
6. escalation_needed (boolean)
7. confidence_score (0-100)"""

            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert emergency response coordinator. Analyze emergency incidents and provide immediate, actionable recommendations. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                
                try:
                    analysis = json.loads(content)
                except json.JSONDecodeError:
                    # Fallback parsing
                    analysis = self._parse_response(content)
                
                return analysis
            else:
                return self._get_fallback_analysis(report)
                
        except Exception as e:
            print(f"✗ Error analyzing emergency with JamAI: {str(e)}")
            return self._get_fallback_analysis(report)
    
    async def get_resource_recommendations(self, 
                                          incident_type: str, 
                                          severity: str,
                                          location: str) -> List[str]:
        """Get recommended resources for incident"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Based on a {severity} severity {incident_type} at {location}, 
            list the necessary emergency resources needed. Respond with a JSON array of resource names."""
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.5,
                "max_tokens": 200
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "[]")
                resources = json.loads(content)
                return resources if isinstance(resources, list) else self._get_default_resources(severity)
            else:
                return self._get_default_resources(severity)
                
        except Exception as e:
            print(f"⚠ Error getting resources: {str(e)}")
            return self._get_default_resources(severity)
    
    async def generate_dispatch_plan(self, analysis: Dict[str, Any], 
                                     report: EmergencyReport) -> Dict[str, Any]:
        """Generate optimal dispatch plan"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Create a dispatch plan for this emergency:
            
Analysis: {json.dumps(analysis)}
Location: {report.location}
Incident: {report.incident_type}

Provide JSON with:
1. primary_dispatch (unit and ETA)
2. backup_dispatch (unit and ETA)
3. coordination_notes (list)
4. public_safety_alerts (list)
5. traffic_management (list)"""
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.6,
                "max_tokens": 500
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                plan = json.loads(content)
                return plan
            else:
                return self._get_fallback_dispatch_plan()
                
        except Exception as e:
            print(f"⚠ Error generating dispatch plan: {str(e)}")
            return self._get_fallback_dispatch_plan()
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse response when JSON parsing fails"""
        return {
            "risk_assessment": 75,
            "immediate_actions": ["Assess scene safety", "Call for additional units"],
            "required_resources": ["Ambulance", "Fire truck", "Police unit"],
            "estimated_response_time": 8,
            "escalation_needed": True,
            "confidence_score": 60
        }
    
    def _get_fallback_analysis(self, report: EmergencyReport) -> Dict[str, Any]:
        """Provide fallback analysis"""
        severity_map = {
            "critical": 95,
            "high": 75,
            "medium": 50,
            "low": 25
        }
        
        return {
            "risk_assessment": severity_map.get(report.severity, 50),
            "immediate_actions": [
                "Scene assessment",
                "Emergency services coordination",
                "Public safety measures"
            ],
            "required_resources": ["Ambulance", "Fire Department", "Police"],
            "estimated_response_time": 5 if report.severity in ["critical", "high"] else 10,
            "escalation_needed": report.severity in ["critical", "high"],
            "confidence_score": 70
        }
    
    def _get_default_resources(self, severity: str) -> List[str]:
        """Get default resources based on severity"""
        resources = {
            "critical": ["Ambulance", "Fire truck", "Police units", "Hazmat team"],
            "high": ["Ambulance", "Fire truck", "Police unit"],
            "medium": ["Ambulance", "Police unit"],
            "low": ["Standard ambulance"]
        }
        return resources.get(severity, ["Standard ambulance"])
    
    def _get_fallback_dispatch_plan(self) -> Dict[str, Any]:
        """Provide fallback dispatch plan"""
        return {
            "primary_dispatch": {
                "unit": "Unit-1",
                "eta": "5 minutes"
            },
            "backup_dispatch": {
                "unit": "Unit-2",
                "eta": "8 minutes"
            },
            "coordination_notes": [
                "Scene assessment priority",
                "Communication with caller",
                "Traffic management"
            ],
            "public_safety_alerts": ["Road closure notice"],
            "traffic_management": ["Redirect traffic"]
        }
    
    async def close(self):
        """Close JamAI client connection"""
        await self.client.aclose()


# Global JamAI instance
jamai = JamAIIntegration()

# Incident tracking
active_incidents: Dict[str, Dict[str, Any]] = {}
incident_counter = 0


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize JamAI on startup"""
    await jamai.initialize()
    print("✓ Emergency Response System started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await jamai.close()
    print("✓ Emergency Response System shutdown")


@app.post("/api/emergency/report", response_model=EmergencyResponse)
async def submit_emergency_report(report: EmergencyReport) -> EmergencyResponse:
    """Submit and analyze emergency report using JamAI"""
    global incident_counter
    
    try:
        # Generate incident ID
        incident_counter += 1
        incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{incident_counter}"
        
        # Set timestamp if not provided
        if not report.timestamp:
            report.timestamp = datetime.utcnow().isoformat()
        
        # Analyze with JamAI
        analysis = await jamai.analyze_emergency(report)
        
        # Get resource recommendations
        resources = await jamai.get_resource_recommendations(
            report.incident_type,
            report.severity,
            report.location
        )
        
        # Generate dispatch plan
        dispatch_plan = await jamai.generate_dispatch_plan(analysis, report)
        
        # Calculate priority score
        risk_assessment = analysis.get("risk_assessment", 50)
        priority_score = min(100, max(0, risk_assessment))
        
        # Prepare response
        response = EmergencyResponse(
            incident_id=incident_id,
            status="ACTIVE",
            recommended_actions=analysis.get("immediate_actions", []),
            resources_required=resources,
            estimated_arrival_time=f"{analysis.get('estimated_response_time', 5)} minutes",
            priority_score=priority_score,
            ai_analysis={
                "risk_assessment": analysis.get("risk_assessment", 50),
                "escalation_needed": analysis.get("escalation_needed", False),
                "confidence_score": analysis.get("confidence_score", 70),
                "dispatch_plan": dispatch_plan
            }
        )
        
        # Store incident
        active_incidents[incident_id] = {
            "report": report.dict(),
            "response": response.dict(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        return response
        
    except Exception as e:
        print(f"✗ Error submitting emergency report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emergency/incident/{incident_id}")
async def get_incident_status(incident_id: str):
    """Get incident status and details"""
    if incident_id not in active_incidents:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return active_incidents[incident_id]


@app.get("/api/emergency/active-incidents")
async def get_active_incidents():
    """Get all active incidents"""
    return {
        "total_active": len(active_incidents),
        "incidents": [
            {
                "incident_id": id,
                "priority_score": data["response"]["priority_score"],
                "status": data["response"]["status"],
                "created_at": data["created_at"]
            }
            for id, data in active_incidents.items()
        ]
    }


@app.put("/api/emergency/incident/{incident_id}/status")
async def update_incident_status(incident_id: str, status: str):
    """Update incident status"""
    if incident_id not in active_incidents:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    valid_statuses = ["ACTIVE", "IN_PROGRESS", "RESOLVED", "CANCELLED"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")
    
    active_incidents[incident_id]["response"]["status"] = status
    active_incidents[incident_id]["updated_at"] = datetime.utcnow().isoformat()
    
    return {
        "incident_id": incident_id,
        "status": status,
        "updated_at": active_incidents[incident_id]["updated_at"]
    }


@app.post("/api/emergency/update-analysis/{incident_id}")
async def update_analysis(incident_id: str, additional_info: Dict[str, Any]):
    """Update analysis with new information"""
    if incident_id not in active_incidents:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident = active_incidents[incident_id]
    original_report = EmergencyReport(**incident["report"])
    
    # Update with additional details
    if original_report.additional_details:
        original_report.additional_details.update(additional_info)
    else:
        original_report.additional_details = additional_info
    
    # Re-analyze with updated information
    updated_analysis = await jamai.analyze_emergency(original_report)
    
    # Update incident
    incident["response"]["ai_analysis"] = {
        "risk_assessment": updated_analysis.get("risk_assessment", 50),
        "escalation_needed": updated_analysis.get("escalation_needed", False),
        "confidence_score": updated_analysis.get("confidence_score", 70),
        "dispatch_plan": await jamai.generate_dispatch_plan(updated_analysis, original_report)
    }
    incident["updated_at"] = datetime.utcnow().isoformat()
    
    return incident


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Emergency Response System with JamAI",
        "timestamp": datetime.utcnow().isoformat(),
        "active_incidents": len(active_incidents)
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "service": "Emergency Response System with JamAI Integration",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/emergency/report": "Submit emergency report",
            "GET /api/emergency/incident/{incident_id}": "Get incident details",
            "GET /api/emergency/active-incidents": "Get all active incidents",
            "PUT /api/emergency/incident/{incident_id}/status": "Update incident status",
            "POST /api/emergency/update-analysis/{incident_id}": "Update analysis with new information",
            "GET /api/health": "Health check",
            "GET /": "API documentation"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
