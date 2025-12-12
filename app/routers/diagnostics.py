from fastapi import APIRouter, Body, HTTPException
from app.core.clients import http_client, ha_api
from app.core.config import settings
from app.models.common import SuccessResponse
from app.models.system import (
    GetConfigEntryDiagnosticsRequest, GetDeviceDiagnosticsRequest,
    ListAvailableDiagnosticsRequest
)

router = APIRouter(tags=["diagnostics"])

@router.post("/ha_get_config_entry_diagnostics", operation_id="ha_get_config_entry_diagnostics", summary="Get config entry diagnostics")
async def ha_get_config_entry_diagnostics(request: GetConfigEntryDiagnosticsRequest = Body(...)):
    """Download diagnostic data for a config entry."""
    url = f"{settings.HA_URL}/config/config_entries/entry/{request.entry_id}/diagnostics"
    response = await http_client.get(url)
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Diagnostics not supported for this entry")
    response.raise_for_status()
    
    return SuccessResponse(
        message=f"Diagnostics for {request.entry_id}",
        data=response.json()
    )

@router.post("/ha_get_device_diagnostics", operation_id="ha_get_device_diagnostics", summary="Get device diagnostics")
async def ha_get_device_diagnostics(request: GetDeviceDiagnosticsRequest = Body(...)):
    """Download diagnostic data for a device."""
    url = f"{settings.HA_URL}/config/device_registry/device/{request.device_id}/diagnostics"
    response = await http_client.get(url)
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Diagnostics not supported for this device")
    response.raise_for_status()
    
    return SuccessResponse(
        message=f"Diagnostics for {request.device_id}",
        data=response.json()
    )

@router.post("/ha_list_available_diagnostics", operation_id="ha_list_available_diagnostics", summary="List available diagnostics")
async def ha_list_available_diagnostics(request: ListAvailableDiagnosticsRequest = Body(...)):
    """List integrations and devices that support diagnostics."""
    # Fetch config entries and devices
    config_entries = await ha_api.call_api("GET", "/config/config_entries")
    
    # Simple list return for now, mimicking server.py logic
    return SuccessResponse(
        message="List of diagnostics candidates",
        data={"entries": config_entries}
    )
