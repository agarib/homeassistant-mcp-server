from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class GetScriptRequest(BaseModel):
    script_id: str = Field(..., description="Script ID (e.g., script.my_script)")

class SetScriptRequest(BaseModel):
    script_id: str = Field(..., description="Script ID to create/update")
    alias: Optional[str] = Field(None, description="Friendly name")
    description: Optional[str] = Field(None, description="Description")
    sequence: list = Field(default_factory=list, description="Action sequence")
    mode: Optional[str] = Field("single", description="Execution mode: single, restart, queued, parallel")
    icon: Optional[str] = Field(None, description="Icon")
    fields: Optional[Dict[str, Any]] = Field(None, description="Input fields schema")

class RemoveScriptRequest(BaseModel):
    script_id: str = Field(..., description="Script ID to delete")
    confirm: bool = Field(False, description="Must be true to confirm deletion")
