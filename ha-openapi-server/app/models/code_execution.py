from typing import List, Optional
from pydantic import BaseModel, Field

class ExecutePythonRequest(BaseModel):
    code: str = Field(..., description="Python code to execute")
    return_stdout: bool = Field(True, description="Return stdout output")
    return_plots: bool = Field(True, description="Return matplotlib plots as base64")

class AnalyzeStatesRequest(BaseModel):
    domain: Optional[str] = Field(None, description="Filter by domain (e.g., 'light', 'sensor')")
    include_attributes: bool = Field(True, description="Include entity attributes")
    query: Optional[str] = Field(None, description="Pandas query filter (e.g., \"state == 'on'\")")

class PlotSensorHistoryRequest(BaseModel):
    entity_ids: List[str] = Field(..., description="Sensor entity IDs to plot")
    hours: int = Field(25, description="Hours of history to plot")
    chart_type: str = Field("line", description="Chart type: line, bar, scatter")
    title: Optional[str] = Field(None, description="Chart title")
