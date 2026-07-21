from typing import Optional, List
from pydantic import BaseModel, Field

class GetEntityRequest(BaseModel):
    entity_id: Optional[str] = Field(None, description="Specific entity ID (omit for all)")
    domain: Optional[str] = Field(None, description="Filter by domain (e.g., 'sensor')")

class SetEntityRequest(BaseModel):
    entity_id: str = Field(..., description="Entity ID to update")
    name: Optional[str] = Field(None, description="New display name")
    icon: Optional[str] = Field(None, description="New icon")
    area_id: Optional[str] = Field(None, description="Area ID to assign")
    disabled_by: Optional[str] = Field(None, description="Disable reason: 'user', 'integration', or None to enable")
    hidden_by: Optional[str] = Field(None, description="Hide reason: 'user', 'integration', or None to unhide")
    new_entity_id: Optional[str] = Field(None, description="New entity ID (rename)")

class RemoveEntityRequest(BaseModel):
    entity_id: str = Field(..., description="Entity ID to remove from registry")

class GetEntityExposureRequest(BaseModel):
    entity_id: Optional[str] = Field(None, description="Specific entity ID (omit for all)")
