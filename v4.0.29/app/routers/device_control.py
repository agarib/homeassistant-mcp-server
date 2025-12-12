from fastapi import APIRouter, Body
from app.core.clients import ha_api
from app.models.common import SuccessResponse
from app.models.device import (
    ControlLightRequest, ControlSwitchRequest, 
    ControlClimateRequest, ControlCoverRequest,
    ControlVacuumRequest, ControlFanRequest, ControlMediaRequest
)

router = APIRouter(tags=["device_control"])

@router.post("/ha_control_light", operation_id="ha_control_light", summary="Control a light entity")
async def ha_control_light(request: ControlLightRequest = Body(...)):
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

@router.post("/ha_control_switch", operation_id="ha_control_switch", summary="Control a switch entity")
async def ha_control_switch(request: ControlSwitchRequest = Body(...)):
    """Control switch entities."""
    result = await ha_api.call_service(
        "switch",
        request.action,
        entity_id=request.entity_id
    )
    return SuccessResponse(message=f"Switch {request.action} executed for {request.entity_id}", data=result)

@router.post("/ha_control_cover", operation_id="ha_control_cover", summary="Control a cover entity")
async def ha_control_cover(request: ControlCoverRequest = Body(...)):
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

@router.post("/ha_control_climate", operation_id="ha_control_climate", summary="Control a climate entity")
async def ha_control_climate(request: ControlClimateRequest = Body(...)):
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

@router.post("/ha_control_vacuum", operation_id="ha_control_vacuum", summary="Control a vacuum entity")
async def ha_control_vacuum(request: ControlVacuumRequest = Body(...)):
    """Control vacuum cleaners."""
    result = await ha_api.call_service(
        "vacuum",
        request.action,
        entity_id=request.entity_id
    )
    return SuccessResponse(message=f"Vacuum {request.action} executed for {request.entity_id}", data=result)

@router.post("/ha_control_fan", operation_id="ha_control_fan", summary="Control a fan entity")
async def ha_control_fan(request: ControlFanRequest = Body(...)):
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

@router.post("/ha_control_media_player", operation_id="ha_control_media_player", summary="Control a media player")
async def ha_control_media_player(request: ControlMediaRequest = Body(...)):
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
