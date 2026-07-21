from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class GetScriptRequest(BaseModel):
    script_id: Optional[str] = Field(default=None, description="Script ID to retrieve (omit for all scripts)")

class SetScriptRequest(BaseModel):
    script_id: str = Field(..., description="Script ID to create or update")
    alias: Optional[str] = Field(default=None, description="Script name/alias")
    sequence: Optional[List[Dict[str, Any]]] = Field(default=None, description="Script action sequence")
    description: Optional[str] = Field(default=None, description="Script description")
    mode: Optional[str] = Field(default=None, description="Script mode: single, restart, queued, parallel")
    icon: Optional[str] = Field(default=None, description="Script icon (mdi:xxx)")
    fields: Optional[Dict[str, Any]] = Field(default=None, description="Script fields/template variables")

class RemoveScriptRequest(BaseModel):
    confirm: bool = Field(default=False, description="Confirm deletion (must be true)")
    script_id: str = Field(..., description="Script ID to remove")
