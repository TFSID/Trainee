"""
FastAPI application for CVE Analyst
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from config.settings import CVEConfig
from api.cve_analyst_api import CVEAnalystAPI

def create_fastapi_app(config: CVEConfig) -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="CVE Analyst API", 
        version="1.0.0",
        description="AI-powered CVE analysis and security recommendations"
    )
    
    analyst = CVEAnalystAPI(config)
    
    class CVEAnalysisRequest(BaseModel):
        cve_id: str
        instruction: str = "Analyze this CVE and provide security recommendations"
    
    class CVEAnalysisResponse(BaseModel):
        cve_id: str
        analysis: str
        timestamp: str
    
    @app.post("/analyze", response_model=CVEAnalysisResponse)
    async def analyze_cve(request: CVEAnalysisRequest):
        """Analyze a CVE and provide security recommendations"""
        try:
            result = analyst.analyze_cve(request.cve_id, request.instruction)
            return CVEAnalysisResponse(
                cve_id=request.cve_id,
                analysis=result,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/cve/{cve_id}")
    async def get_cve_info(cve_id: str):
        """Get CVE information from database"""
        cve_info = analyst.get_cve_info(cve_id)
        if not cve_info:
            raise HTTPException(status_code=404, detail="CVE not found")
        return cve_info
    
    @app.get("/recent-cves")
    async def get_recent_cves(limit: int = 10):
        """Get recent CVEs"""
        return analyst.get_recent_cves(limit=limit)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy", 
            "timestamp": datetime.now().isoformat(),
            "model_loaded": analyst.model is not None
        }
    
    return app
