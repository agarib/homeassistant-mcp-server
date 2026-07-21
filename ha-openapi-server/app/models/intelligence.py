from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AnalyzeHomeContextRequest(BaseModel):
    pass  # No parameters needed - analyzes entire home

class ActivityRecognitionRequest(BaseModel):
    rooms: Optional[List[str]] = Field(None, description="Rooms to analyze (default: all, currently not implemented)")

class ComfortOptimizationRequest(BaseModel):
    room: str = Field(..., description="Room to optimize")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences (temp, brightness, etc.)")

class EnergyIntelligenceRequest(BaseModel):
    period: Optional[str] = Field("day", description="Analysis period: day, week, month (currently not implemented)")
    suggest_savings: bool = Field(True, description="Provide energy-saving suggestions")
