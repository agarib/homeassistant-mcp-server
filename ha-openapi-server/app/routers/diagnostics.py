from fastapi import APIRouter, Body, HTTPException
from app.core.clients import http_client, ha_api, get_ws_client
from app.core.config import settings
from app.models.common import SuccessResponse
from app.models.system import (
    GetConfigEntryDiagnosticsRequest, GetDeviceDiagnosticsRequest,
    ListAvailableDiagnosticsRequest
)

router = APIRouter(tags=["diagnostics"])


@router.post("/get_config_entry_diagnostics", operation_id="get_config_entry_diagnostics", summary="Get config entry diagnostics")
async def get_config_entry_diagnostics(request: GetConfigEntryDiagnosticsRequest = Body(...)):
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


@router.post("/get_device_diagnostics", operation_id="get_device_diagnostics", summary="Get device diagnostics")
async def get_device_diagnostics(request: GetDeviceDiagnosticsRequest = Body(...)):
    """Download diagnostic data for a device."""
    # HA has no per-device diagnostics REST endpoint; diagnostics are per config entry.
    # We look up the device's config_entry_id, then download diagnostics for that entry.
    ws = await get_ws_client()
    devices = await ws.call_command("config/device_registry/list")
    device = None
    for d in devices:
        if d.get("id") == request.device_id:
            device = d
            break

    if not device:
        raise HTTPException(status_code=404, detail=f"Device {request.device_id} not found in registry")

    config_entry_ids = device.get("config_entries", [])
    if not config_entry_ids:
        raise HTTPException(status_code=404, detail="Diagnostics not supported for this device (no config entry)")

    entry_id = config_entry_ids[0]
    url = f"{settings.HA_URL}/config/config_entries/entry/{entry_id}/diagnostics"
    response = await http_client.get(url)
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Diagnostics not supported for this device")
    response.raise_for_status()

    return SuccessResponse(
        message=f"Diagnostics for device {request.device_id} (entry {entry_id})",
        data=response.json()
    )


@router.post("/list_available_diagnostics", operation_id="list_available_diagnostics", summary="List available diagnostics")
async def list_available_diagnostics(request: ListAvailableDiagnosticsRequest = Body(...)):
    """List integrations and devices that support diagnostics."""
    # Fetch config entries via REST (correct path: /config/config_entries/entry)
    config_entries = await ha_api.call_api("GET", "/config/config_entries/entry")

    # Fetch devices via WebSocket
    ws = await get_ws_client()
    devices = await ws.call_command("config/device_registry/list")

    # Filter config entries that support diagnostics
    diag_entries = [
        {
            "entry_id": e.get("entry_id"),
            "domain": e.get("domain"),
            "title": e.get("title"),
            "state": e.get("state"),
            "supports_diagnostics": e.get("supports_diagnostics", False),
        }
        for e in config_entries
        if e.get("supports_diagnostics")
    ]

    # If integration_filter provided, apply it
    if request.integration_filter:
        filt = request.integration_filter.lower()
        diag_entries = [e for e in diag_entries if filt in e["domain"].lower() or filt in e["title"].lower()]

    # Build a set of config entry IDs that support diagnostics
    diag_entry_ids = {e["entry_id"] for e in diag_entries}

    # Map devices to their config entries
    diag_devices = [
        {
            "device_id": d.get("id"),
            "name": d.get("name") or d.get("name_by_user") or "Unnamed",
            "config_entry_ids": d.get("config_entries", []),
            "area_id": d.get("area_id"),
        }
        for d in devices
        if any(ce in diag_entry_ids for ce in d.get("config_entries", []))
    ]

    return SuccessResponse(
        message=f"Found {len(diag_entries)} config entries and {len(diag_devices)} devices with diagnostics",
        data={
            "entries": diag_entries,
            "devices": diag_devices,
        }
    )