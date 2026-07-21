import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from fastapi import APIRouter, Body, HTTPException
from app.core.clients import ha_api, get_ws_client
from app.core.config import settings
from app.models.common import SuccessResponse
from app.models.history_logs import (
    GetHistoryRequest, GetLogsRequest, GetAutomationTracesRequest
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["history_logs"])

@router.post("/get_history", operation_id="get_history", summary="Get entity history data")
async def get_history(request: GetHistoryRequest = Body(...)):
    """Retrieve historical state data for entities via HA REST /history/period.

    Uses the HA REST API (not the supervisor proxy) to fetch state history.
    Returns a list of lists (one per entity_id), each containing state dicts
    with 'state', 'last_changed', 'last_updated', and 'attributes'.
    """
    # Determine time range
    if request.start_time:
        # Accept ISO 8601 with or without 'Z'/'timezone'
        ts = request.start_time
        # Ensure it's a valid timestamp string; pass through to HA
        start_str = ts.replace(" ", "T")
    else:
        hours = request.hours or 24
        start_dt = datetime.now(timezone.utc) - timedelta(hours=hours)
        start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S")

    # Build the /history/period/<timestamp> URL with query params
    endpoint = f"/history/period/{quote(start_str)}"
    params = []
    if request.entity_ids:
        # Filter to specific entities
        for eid in request.entity_ids:
            params.append(f"filter_entity_id={quote(eid)}")
    if request.minimal_response:
        params.append("minimal_response")
    if request.significant_changes_only:
        params.append("significant_changes_only")
    # End time defaults to now (HA default); could be extended later
    if params:
        endpoint += "?" + "&".join(params)

    try:
        result = await ha_api.call_api("GET", endpoint)
        # result is a list of lists (one per entity)
        return SuccessResponse(
            message=f"Retrieved history for {len(result)} entities",
            data=result
        )
    except Exception as e:
        logger.error(f"Error fetching history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"History fetch failed: {e}")

@router.post("/get_automation_traces", operation_id="get_automation_traces", summary="Get automation execution traces")
async def get_automation_traces(request: GetAutomationTracesRequest = Body(...)):
    """Retrieve execution traces for automations and scripts."""
    ws = await get_ws_client()
    
    try:
        if request.trace_id:
            result = await ws.call_command(
                "trace/get",
                domain=request.domain or "automation",
                item_id=request.automation_id.replace("automation.","") if request.automation_id else "",
                run_id=request.trace_id
            )
            return SuccessResponse(message=f"Retrieved trace {request.trace_id}", data=result)
        else:
            params = {"domain": request.domain or "automation"}
            if request.automation_id:
                params["item_id"] = request.automation_id.replace("automation.", "")
            result = await ws.call_command("trace/list", **params)
            traces = result if isinstance(result, list) else []
            if request.limit:
                traces = traces[-request.limit:]
            return SuccessResponse(message=f"Found {len(traces)} traces", data=traces)
    except Exception as e:
        logger.error(f"Error getting traces: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))