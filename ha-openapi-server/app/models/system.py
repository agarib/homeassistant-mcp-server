from typing import List, Optional
from pydantic import BaseModel, Field

# System Router Models
class GetSystemLogsNewRequest(BaseModel):
    level: Optional[str] = Field(default=None, description="Log level filter: debug, info, warning, error, critical")
    lines: Optional[int] = Field(default=100, description="Number of lines to return")

class GetIntegrationStatusNewRequest(BaseModel):
    integration: Optional[str] = Field(default=None, description="Integration domain to check")

class RestartHomeAssistantRequest(BaseModel):
    confirm: bool = Field(default=False, description="Confirm restart (must be true)")

class CheckConfigRequest(BaseModel):
    pass

class GetSystemHealthRequest(BaseModel):
    pass

# Diagnostics Router Models
class GetConfigEntryDiagnosticsRequest(BaseModel):
    entry_id: str = Field(..., description="Config entry ID")

class GetDeviceDiagnosticsRequest(BaseModel):
    device_id: str = Field(..., description="Device ID")

class ListAvailableDiagnosticsRequest(BaseModel):
    integration_filter: Optional[str] = Field(default=None, description="Filter by integration domain")

# Repairs
class GetRepairsRequest(BaseModel):
    active_only: bool = Field(default=True, description="Only show active repair issues")
