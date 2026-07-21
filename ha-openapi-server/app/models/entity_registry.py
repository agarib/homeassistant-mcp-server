from typing import Optional
from pydantic import BaseModel, Field

class GetEntityRequest(BaseModel):
    entity_id: Optional[str] = Field(default=None, description="Specific entity ID to look up")
    domain: Optional[str] = Field(default=None, description="Filter by domain (e.g., light, sensor)")

class SetEntityRequest(BaseModel):
    entity_id: str = Field(..., description="Entity ID to modify")
    name: Optional[str] = Field(default=None, description="New entity name")
    icon: Optional[str] = Field(default=None, description="New entity icon")
    area_id: Optional[str] = Field(default=None, description="Area ID to assign")
    disabled_by: Optional[str] = Field(default=None, description="Disable reason: 'user' to disable, None to enable")
    hidden_by: Optional[str] = Field(default=None, description="Hide reason: 'user' to hide, None to unhide")
    new_entity_id: Optional[str] = Field(default=None, description="New entity ID to rename to")

class RemoveEntityRequest(BaseModel):
    entity_id: str = Field(..., description="Entity ID to remove")

class GetEntityExposureRequest(BaseModel):
    entity_id: str = Field(..., description="Entity ID to check exposure for")
