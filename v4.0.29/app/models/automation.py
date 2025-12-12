from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

# ============================================================================
# Automations
# ============================================================================

class ListAutomationsRequest(BaseModel):
    enabled_only: Optional[bool] = Field(False, description="Only show enabled automations")

class TriggerAutomationRequest(BaseModel):
    automation_id: str = Field(..., description="Automation entity ID")
    skip_condition: Optional[bool] = Field(False, description="Skip conditions and trigger directly")

class CreateAutomationRequest(BaseModel):
    alias: str = Field(..., description="Friendly name for the automation")
    description: Optional[str] = Field("", description="Description of what the automation does")
    mode: str = Field("single", description="Execution mode: single, restart, queued, parallel")
    triggers: list = Field(..., min_length=1, description="List of triggers")
    conditions: list = Field([], description="List of conditions")
    actions: list = Field(..., min_length=1, description="List of actions")

class UpdateAutomationRequest(BaseModel):
    automation_id: str = Field(..., description="Automation entity ID to update")
    alias: Optional[str] = Field(None, description="Friendly name")
    description: Optional[str] = Field(None, description="Description")
    triggers: Optional[list] = Field(None, min_length=1)
    conditions: Optional[list] = Field(None)
    actions: Optional[list] = Field(None, min_length=1)

class DeleteAutomationRequest(BaseModel):
    automation_id: str = Field(..., description="Automation entity ID to delete")

class ToggleAutomationRequest(BaseModel):
    automation_id: str = Field(..., description="Automation entity ID to toggle")
    enable: bool = Field(..., description="True to enable, False to disable")

class ReloadAutomationsRequest(BaseModel):
    validate_only: bool = Field(False, description="Only validate YAML without reloading")

class GetAutomationDetailsRequest(BaseModel):
    automation_id: str = Field(..., description="Automation entity ID (e.g., automation.turn_on_lights)")

# ============================================================================
# Scenes
# ============================================================================

class CreateSceneRequest(BaseModel):
    scene_id: str = Field(..., description="Scene ID (e.g., scene.movie_time)")
    entities: Dict[str, Dict[str, Any]] = Field(..., description="Entity states to capture")

class ActivateSceneRequest(BaseModel):
    scene_id: str = Field(..., description="Scene entity ID to activate")

class ListScenesRequest(BaseModel):
    pass
