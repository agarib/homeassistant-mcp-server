from typing import Optional, List
from pydantic import BaseModel, Field

class GetHistoryRequest(BaseModel):
    entity_ids: Optional[List[str]] = Field(None, description="Specific entity IDs")
    hours: Optional[int] = Field(None, description="Hours of history to retrieve")
    start_time: Optional[str] = Field(None, description="Start time ISO format (overrides hours)")
    minimal_response: Optional[bool] = Field(False, description="Return minimal response")
    significant_changes_only: Optional[bool] = Field(False, description="Only significant state changes")

class GetLogsRequest(BaseModel):
    source: Optional[str] = Field("core", description="Log source: 'core' or 'supervisor'")
    tail_lines: Optional[int] = Field(None, description="Only return last N lines")
    filter: Optional[str] = Field(None, description="Filter lines containing text (case-insensitive)")

class GetAutomationTracesRequest(BaseModel):
    trace_id: Optional[str] = Field(None, description="Specific trace run_id (requires domain+automation_id)")
    automation_id: Optional[str] = Field(None, description="Filter by automation entity ID")
    domain: Optional[str] = Field("automation", description="Domain: automation or script")
    limit: Optional[int] = Field(None, description="Max traces to return")
