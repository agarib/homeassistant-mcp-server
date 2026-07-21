from fastapi import APIRouter
from app.core.clients import ha_api
from app.models.common import SuccessResponse
from app.models.device import (
    DiscoverDevicesRequest, GetDeviceStateRequest, 
    GetAreaDevicesRequest, GetStatesRequest, 
    ListAreasRequest, ListDevicesRequest, CallServiceRequest
)

router = APIRouter(tags=["discovery"])

@router.post("/list_entities", operation_id="list_entities", summary="List all entities")
async def list_entities():
    """List all entities currently tracking state."""
    states = await ha_api.get_states()
    return SuccessResponse(
        message=f"Found {len(states)} entities",
        data=[
            {
                "entity_id": s["entity_id"],
                "state": s["state"],
                "attributes": s.get("attributes", {})
            } for s in states
        ]
    )

@router.post("/get_entity_state", operation_id="get_entity_state", summary="Get entity state")
async def get_entity_state(request: GetDeviceStateRequest):
    """Get the current state of a specific entity."""
    state = await ha_api.get_states(request.entity_id)
    return SuccessResponse(
        message=f"State for {request.entity_id}",
        data=state
    )

@router.post("/get_services", operation_id="get_services", summary="Get available services")
async def get_services():
    """List all available services by domain."""
    services = await ha_api.get_services()
    return SuccessResponse(
        message=f"Found {len(services)} service domains",
        data=services
    )

@router.post("/call_service", operation_id="call_service", summary="Call a service")
async def call_service(request: CallServiceRequest):
    """Generic tool to call any Home Assistant service."""
    result = await ha_api.call_service(
        request.domain,
        request.service,
        entity_id=request.entity_id,
        **(request.service_data or {})
    )
    return SuccessResponse(
        message=f"Called service {request.domain}.{request.service}",
        data=result
    )

@router.post("/list_areas", operation_id="list_areas", summary="List configured areas")
async def list_areas():
    """List all areas configured in Home Assistant."""
    # Note: Modern HA uses WebSocket/Registry for this, implementing via template/service fallback or ws
    # For now, using direct API simulation or known registries if available
    # Using the fix from v4.0.28: specific registry endpoints via WebSocket if possible
    # But since we're in routers, we use ha_api fallback mostly.
    
    # Actually, as per v4.0.28 fix, we should use WebSocket for registry if available
    # For this refactor, let's stick to ha_api wrappers but note the v4.0.28 fix:
    # "New: await ws_client.call_command('config/area_registry/list')"
    
    from app.core.clients import get_ws_client
    ws = await get_ws_client()
    areas = await ws.call_command("config/area_registry/list")
    
    # Sanitize None values to empty strings for string fields
    sanitized_areas = []
    for area in areas:
        sanitized_area = {}
        for key, value in area.items():
            # Convert None to empty string for common string fields
            if value is None and key in ["name", "area_id", "picture", "icon"]:
                sanitized_area[key] = ""
            else:
                sanitized_area[key] = value
        sanitized_areas.append(sanitized_area)
    
    return SuccessResponse(
        message=f"Found {len(sanitized_areas)} areas",
        data=sanitized_areas
    )

@router.post("/list_devices", operation_id="list_devices", summary="List devices")
async def list_devices():
    """List all devices in the device registry."""
    from app.core.clients import get_ws_client
    ws = await get_ws_client()
    devices = await ws.call_command("config/device_registry/list")
    
    # Sanitize None values to empty strings for string fields to prevent client-side errors
    sanitized_devices = []
    for device in devices:
        sanitized_device = {}
        for key, value in device.items():
            # Convert None to empty string for common string fields
            if value is None and key in ["manufacturer", "model", "name", "name_by_user", "area_id", "sw_version", "hw_version"]:
                sanitized_device[key] = ""
            else:
                sanitized_device[key] = value
        sanitized_devices.append(sanitized_device)
    
    return SuccessResponse(
        message=f"Found {len(sanitized_devices)} devices",
        data=sanitized_devices
    )
