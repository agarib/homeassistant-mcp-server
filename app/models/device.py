from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# ============================================================================
# Device Control
# ============================================================================

class ControlLightRequest(BaseModel):
    entity_id: str = Field(..., description="Light entity ID (e.g., light.living_room)")
    action: str = Field(..., description="Action: turn_on, turn_off, toggle")
    brightness: Optional[int] = Field(None, description="Brightness 0-255")
    rgb_color: Optional[List[int]] = Field(None, description="RGB color [R, G, B]")
    color_temp: Optional[int] = Field(None, description="Color temperature in mireds")
    transition: Optional[int] = Field(None, description="Transition time in seconds")

class ControlSwitchRequest(BaseModel):
    entity_id: str = Field(..., description="Switch entity ID (e.g., switch.fan)")
    action: str = Field(..., description="Action: turn_on, turn_off, toggle")

class ControlClimateRequest(BaseModel):
    entity_id: str = Field(..., description="Climate entity ID (e.g., climate.bedroom)")
    action: str = Field(..., description="Action: turn_on, turn_off, set_temperature, set_hvac_mode")
    temperature: Optional[float] = Field(None, description="Target temperature")
    hvac_mode: Optional[str] = Field(None, description="HVAC mode: heat, cool, auto, off")
    fan_mode: Optional[str] = Field(None, description="Fan mode: auto, low, medium, high")

class ControlCoverRequest(BaseModel):
    entity_id: str = Field(..., description="Cover entity ID (e.g., cover.garage)")
    action: str = Field(..., description="Action: open_cover, close_cover, stop_cover, set_cover_position")
    position: Optional[int] = Field(None, description="Position 0-100")

class ControlVacuumRequest(BaseModel):
    entity_id: str = Field(..., description="Vacuum entity ID")
    action: str = Field(..., description="Action: start, stop, pause, return_to_base")

class ControlFanRequest(BaseModel):
    entity_id: str = Field(..., description="Fan entity ID")
    action: str = Field(..., description="Action: turn_on, turn_off, set_percentage")
    percentage: Optional[int] = Field(None, description="Speed percentage 0-100")

class ControlMediaRequest(BaseModel):
    entity_id: str = Field(..., description="Media player entity ID")
    action: str = Field(..., description="Action: play_pause, stop, prev, next, vol_up, vol_down, mute")
    volume_level: Optional[float] = Field(None, description="Volume level 0.0-1.0")
    media_content_id: Optional[str] = Field(None, description="Media URL or ID to play")
    media_content_type: Optional[str] = Field(None, description="Media type (music, video, etc)")

# ============================================================================
# Discovery & State
# ============================================================================

class DiscoverDevicesRequest(BaseModel):
    domain: Optional[str] = Field(None, description="Filter by domain (light, switch, etc.)")
    area: Optional[str] = Field(None, description="Filter by area name")

class GetDeviceStateRequest(BaseModel):
    entity_id: str = Field(..., description="Entity ID to get state for")

class GetAreaDevicesRequest(BaseModel):
    area_name: str = Field(..., description="Area name (e.g., 'living room')")

class GetStatesRequest(BaseModel):
    domain: Optional[str] = Field(None, description="Filter by domain")
    limit: Optional[int] = Field(None, description="Limit number of results")

class ListAreasRequest(BaseModel):
    pass

class ListDevicesRequest(BaseModel):
    pass

class CallServiceRequest(BaseModel):
    domain: str = Field(..., description="Service domain (e.g., light)")
    service: str = Field(..., description="Service name (e.g., turn_on)")
    entity_id: Optional[str] = Field(None, description="Target entity ID")
    service_data: Optional[Dict[str, Any]] = Field(None, description="Additional service data")
