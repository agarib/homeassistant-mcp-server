from fastapi import APIRouter, Body
from app.core.clients import ha_api, get_ws_client
from app.models.common import SuccessResponse
from app.models.device import (
    ControlLightRequest, ControlSwitchRequest, 
    ControlClimateRequest, ControlCoverRequest,
    ControlVacuumRequest, ControlFanRequest, ControlMediaRequest
)

router = APIRouter(tags=["device_control"])

@router.post("/control_light", operation_id="control_light", summary="Control a light entity")
async def control_light(request: ControlLightRequest = Body(...)):
    """Control light entities: turn on/off, adjust brightness, change colors."""
    service_data = {}
    if request.brightness is not None:
        service_data["brightness"] = request.brightness
    if request.rgb_color:
        service_data["rgb_color"] = request.rgb_color
    if request.color_temp is not None:
        service_data["color_temp"] = request.color_temp
    if request.transition is not None:
        service_data["transition"] = request.transition
    
    result = await ha_api.call_service(
        "light",
        request.action,
        entity_id=request.entity_id,
        **service_data
    )
    return SuccessResponse(message=f"Light {request.action} executed for {request.entity_id}", data=result)

@router.post("/control_switch", operation_id="control_switch", summary="Control a switch entity")
async def control_switch(request: ControlSwitchRequest = Body(...)):
    """Control switch entities."""
    result = await ha_api.call_service(
        "switch",
        request.action,
        entity_id=request.entity_id
    )
    return SuccessResponse(message=f"Switch {request.action} executed for {request.entity_id}", data=result)

@router.post("/control_cover", operation_id="control_cover", summary="Control a cover entity")
async def control_cover(request: ControlCoverRequest = Body(...)):
    """Control covers (blinds, garage doors)."""
    service_data = {}
    if request.position is not None:
        service_data["position"] = request.position
    
    result = await ha_api.call_service(
        "cover",
        request.action,
        entity_id=request.entity_id,
        **service_data
    )
    return SuccessResponse(message=f"Cover {request.action} executed for {request.entity_id}", data=result)

@router.post("/control_climate", operation_id="control_climate", summary="Control a climate entity")
async def control_climate(request: ControlClimateRequest = Body(...)):
    """Control climate/thermostat entities."""
    service_data = {}
    if request.temperature is not None:
        service_data["temperature"] = request.temperature
    if request.hvac_mode:
        service_data["hvac_mode"] = request.hvac_mode
    if request.fan_mode:
        service_data["fan_mode"] = request.fan_mode
        
    result = await ha_api.call_service(
        "climate",
        request.action,
        entity_id=request.entity_id,
        **service_data
    )
    return SuccessResponse(message=f"Climate {request.action} executed for {request.entity_id}", data=result)

@router.post("/control_vacuum", operation_id="control_vacuum", summary="Control a vacuum entity")
async def control_vacuum(request: ControlVacuumRequest = Body(...)):
    """Control vacuum cleaners."""
    result = await ha_api.call_service(
        "vacuum",
        request.action,
        entity_id=request.entity_id
    )
    return SuccessResponse(message=f"Vacuum {request.action} executed for {request.entity_id}", data=result)

@router.post("/control_fan", operation_id="control_fan", summary="Control a fan entity")
async def control_fan(request: ControlFanRequest = Body(...)):
    """Control fan entities."""
    service_data = {}
    if request.percentage is not None:
        service_data["percentage"] = request.percentage
        
    result = await ha_api.call_service(
        "fan",
        request.action,
        entity_id=request.entity_id,
        **service_data
    )
    return SuccessResponse(message=f"Fan {request.action} executed for {request.entity_id}", data=result)

@router.post("/control_media_player", operation_id="control_media_player", summary="Control a media player")
async def control_media_player(request: ControlMediaRequest = Body(...)):
    """Control media players."""
    service_data = {}
    if request.volume_level is not None:
        service_data["volume_level"] = request.volume_level
    if request.media_content_id:
        service_data["media_content_id"] = request.media_content_id
        service_data["media_content_type"] = request.media_content_type
        
    # Mapping simple actions to service calls
    service = request.action
    if request.action == "play_pause":
        service = "media_play_pause"
    elif request.action == "stop":
        service = "media_stop"
    elif request.action == "prev":
        service = "media_previous_track"
    elif request.action == "next":
        service = "media_next_track"
    elif request.action == "vol_up":
        service = "volume_up"
    elif request.action == "vol_down":
        service = "volume_down"
        
    result = await ha_api.call_service(
        "media_player",
        service,
        entity_id=request.entity_id,
        **service_data
    )
    return SuccessResponse(message=f"Media player {request.action} executed for {request.entity_id}", data=result)


from typing import Optional
from pydantic import BaseModel, Field

class UpdateDeviceRequest(BaseModel):
    device_id: str = Field(..., description="Device registry ID")
    name_by_user: Optional[str] = Field(None, description="User-friendly device name")
    area_id: Optional[str] = Field(None, description="Area ID to assign device to")

@router.post("/update_device", operation_id="update_device", summary="Update device registry entry")
async def update_device(request: UpdateDeviceRequest = Body(...)):
    """Update a device in the HA device registry via WebSocket.

    Can rename (name_by_user) and/or reassign area (area_id).
    """
    ws = await get_ws_client()
    try:
        params = {"device_id": request.device_id}
        if request.name_by_user is not None:
            params["name_by_user"] = request.name_by_user
        if request.area_id is not None:
            params["area_id"] = request.area_id
        result = await ws.call_command("config/device_registry/update", **params)
        return SuccessResponse(
            message=f"Device {request.device_id} updated",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
