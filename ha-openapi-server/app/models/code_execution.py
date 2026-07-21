from typing import List, Optional
from pydantic import BaseModel, Field

class ExecutePythonRequest(BaseModel):
    code: str = Field(..., description="Python code to execute")
    return_plots: bool = Field(default=False, description="Return plot data as base64")
    return_stdout: bool = Field(default=True, description="Return stdout output")

class AnalyzeStatesRequest(BaseModel):
    domain: Optional[str] = Field(default=None, description="Filter by domain (e.g., sensor, light)")
    include_attributes: bool = Field(default=False, description="Include entity attributes")
    query: Optional[str] = Field(default=None, description="Optional pandas query to filter results")

class PlotSensorHistoryRequest(BaseModel):
    entity_ids: List[str] = Field(..., description="List of entity IDs to plot")
    chart_type: Optional[str] = Field(default="line", description="Chart type: line, bar, scatter")
    title: Optional[str] = Field(default=None, description="Chart title")
