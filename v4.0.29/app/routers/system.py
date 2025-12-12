from fastapi import APIRouter, Body
from app.core.clients import ha_api, http_client
from app.models.common import SuccessResponse
from app.models.system import (
    GetSystemLogsNewRequest, GetIntegrationStatusNewRequest,
    RestartHomeAssistantRequest
)

router = APIRouter(tags=["system"])

@router.post("/ha_get_system_logs_diagnostics", operation_id="ha_get_system_logs_diagnostics", summary="Get system logs")
async def ha_get_system_logs(request: GetSystemLogsNewRequest = Body(...)):
    """Read HA core logs via logbook/api."""
    # Logic extracted from server.py (lines ~4816)
    url = f"{ha_api.base_url}/logbook"
    response = await http_client.get(url)
    response.raise_for_status()
    logbook_entries = response.json()
    
    # Filter and format logic
    if request.level:
        logbook_entries = [
            e for e in logbook_entries
            if any(k in str(e).lower() for k in ["error", "fail", "warning", "problem"])
        ]
        
    return SuccessResponse(
        message=f"Retrieved {len(logbook_entries)} log entries",
        data=logbook_entries[-request.lines:]
    )

@router.post("/ha_get_persistent_notifications", operation_id="ha_get_persistent_notifications", summary="Get notifications")
async def ha_get_persistent_notifications():
    """Get persistent notifications."""
    states = await ha_api.get_states()
    notifications = [
        s for s in states if s["entity_id"].startswith("persistent_notification.")
    ]
    return SuccessResponse(
        message=f"Found {len(notifications)} notifications",
        data=notifications
    )

@router.post("/ha_restart_homeassistant", operation_id="ha_restart_homeassistant", summary="Restart HA")
async def ha_restart_homeassistant(request: RestartHomeAssistantRequest = Body(...)):
    """Restart Home Assistant Core."""
    if request.confirm:
        await ha_api.call_service("homeassistant", "restart")
        return SuccessResponse(message="Restart initiated")
    return SuccessResponse(message="Restart not confirmed")
