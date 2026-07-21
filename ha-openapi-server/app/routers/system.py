from fastapi import APIRouter, Body
from app.core.clients import ha_api, http_client, get_ws_client
from app.models.common import SuccessResponse
from app.models.system import (
    GetSystemLogsNewRequest, GetIntegrationStatusNewRequest,
    RestartHomeAssistantRequest, CheckConfigRequest, GetSystemHealthRequest
)

router = APIRouter(tags=["system"])

@router.post("/get_system_logs_diagnostics", operation_id="get_system_logs_diagnostics", summary="Get system logs")
async def ha_get_system_logs(request: GetSystemLogsNewRequest = Body(...)):
    """Read HA core logs via WebSocket system_log/list.

    The supervisor proxy blocks the REST /logbook endpoint (404), so we use
    the WebSocket API command system_log/list which returns the HA core log
    buffer with level, timestamp, message, name, and domain fields.
    """
    ws = await get_ws_client()
    log_entries = await ws.call_command("system_log/list")

    # Filter by level if specified
    if request.level:
        level_lower = request.level.lower()
        log_entries = [
            e for e in log_entries
            if (
                # Direct level field match
                (isinstance(e.get("level"), str) and level_lower in e.get("level", "").lower())
                # Check in message or name fields
                or (isinstance(e.get("message"), str) and level_lower in e.get("message", "").lower())
                or (isinstance(e.get("name"), str) and level_lower in e.get("name", "").lower())
                # Or check for common error/warning keywords
                or (level_lower in ["error", "warning"] and
                    any(k in str(e.get("message", "")).lower() + str(e.get("name", "")).lower()
                        for k in ["error", "fail", "warning", "problem", "exception"]))
            )
        ]

    return SuccessResponse(
        message=f"Retrieved {len(log_entries)} log entries",
        data=log_entries[-request.lines:]
    )

@router.post("/get_persistent_notifications", operation_id="get_persistent_notifications", summary="Get notifications")
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

@router.post("/restart_homeassistant", operation_id="restart_homeassistant", summary="Restart HA")
async def ha_restart_homeassistant(request: RestartHomeAssistantRequest = Body(...)):
    """Restart Home Assistant Core."""
    if request.confirm:
        await ha_api.call_service("homeassistant", "restart")
        return SuccessResponse(message="Restart initiated")
    else:
        return SuccessResponse(message="Restart not confirmed", data={"confirmed": False})

@router.post("/check_config", operation_id="check_config", summary="Check HA configuration")
async def ha_check_config(request: CheckConfigRequest = Body(...)):
    """Check Home Assistant configuration validation."""
    result = await ha_api.call_service("homeassistant", "check_config")
    return SuccessResponse(message="Configuration check initiated", data=result)

@router.post("/system_health", operation_id="system_health", summary="Get system health")
async def ha_system_health(request: GetSystemHealthRequest = Body(...)):
    """Get Home Assistant system health info."""
    # Get config for version info
    config = await ha_api.call_api("GET", "/config")

    # Get states to check if system is responsive
    try:
        states = await ha_api.get_states()
        state = "RUNNING" if states else "UNKNOWN"
    except Exception:
        state = "ERROR"

    return SuccessResponse(
        message="System health retrieved",
        data={
            "state": state,
            "version": config.get("version"),
            "location_name": config.get("location_name"),
            "unit_system": config.get("unit_system", {}).get("length"),
            "time_zone": config.get("time_zone"),
            "components": len(config.get("components", [])),
            "config_dir": config.get("config_dir")
        }
    )

from typing import Optional
from pydantic import BaseModel, Field

class GetRepairsRequest(BaseModel):
    active_only: Optional[bool] = Field(True, description="Only return active (non-dismissed) issues")

@router.post("/get_repairs", operation_id="get_repairs", summary="Get HA repair issues")
async def ha_get_repairs(request: GetRepairsRequest = Body(default_factory=GetRepairsRequest)):
    """List Home Assistant repair issues via WebSocket repairs/list_issues.

    Returns issues raised by integrations (config problems, deprecated config,
    entity issues, etc.). Each issue has: issue_id, domain, active, dismissed,
    learn_more_url, translation_key, etc.
    """
    ws = await get_ws_client()
    try:
        result = await ws.call_command("repairs/list_issues")
        issues = result if isinstance(result, list) else result.get("issues", [])
        if request.active_only:
            issues = [i for i in issues if not i.get("dismissed", False)]
        return SuccessResponse(
            message=f"Found {len(issues)} repair issues",
            data=issues
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
