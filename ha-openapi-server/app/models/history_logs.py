from typing import List, Optional
from pydantic import BaseModel, Field

class GetHistoryRequest(BaseModel):
    start_time: Optional[str] = Field(default=None, description="ISO 8601 start timestamp (default: 24h ago)")
    hours: Optional[float] = Field(default=24, description="Hours to look back from now")
    entity_ids: Optional[List[str]] = Field(default=None, description="Entity IDs to filter by")
    minimal_response: bool = Field(default=True, description="Return minimal response")
    significant_changes_only: bool = Field(default=False, description="Only return significant state changes")

class GetLogsRequest(BaseModel):
    pass

class GetAutomationTracesRequest(BaseModel):
    trace_id: Optional[str] = Field(default=None, description="Specific trace ID to retrieve")
    domain: Optional[str] = Field(default="automation", description="Domain to get traces for")
    automation_id: Optional[str] = Field(default=None, description="Automation entity ID")
    limit: Optional[int] = Field(default=10, description="Max number of traces to return")
