import logging
from fastapi import APIRouter, Body, HTTPException
from app.core.clients import ha_api, get_ws_client
from app.models.common import SuccessResponse
from app.models.entity_registry import (
    GetEntityRequest, SetEntityRequest, RemoveEntityRequest, GetEntityExposureRequest
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["entity_registry"])

@router.post("/get_entity", operation_id="get_entity", summary="Get entity registry information")
async def get_entity(request: GetEntityRequest = Body(...)):
    """Get entity registry information for one or more entities."""
    ws = await get_ws_client()
    
    if request.entity_id:
        result = await ws.call_command("config/entity_registry/get", entity_id=request.entity_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Entity {request.entity_id} not found in registry")
        # Return consistent single-entity format
        return SuccessResponse(
            message=f"Retrieved entity {request.entity_id}",
            data=result
        )
    else:
        result = await ws.call_command("config/entity_registry/list")
        if request.domain:
            result = [e for e in result if e.get("entity_id","").startswith(f"{request.domain}.")]
        return SuccessResponse(
            message=f"Found {len(result)} entities in registry",
            data=result
        )

@router.post("/set_entity", operation_id="set_entity", summary="Update entity registry properties")
async def set_entity(request: SetEntityRequest = Body(...)):
    """Update entity properties in the entity registry."""
    ws = await get_ws_client()
    
    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.icon is not None:
        update_data["icon"] = request.icon
    if request.area_id is not None:
        update_data["area_id"] = request.area_id
    if request.disabled_by is not None:
        update_data["disabled_by"] = request.disabled_by
    if request.hidden_by is not None:
        update_data["hidden_by"] = request.hidden_by
    if request.new_entity_id is not None:
        update_data["new_entity_id"] = request.new_entity_id
    
    result = await ws.call_command(
        "config/entity_registry/update",
        entity_id=request.entity_id,
        **update_data
    )
    
    return SuccessResponse(
        message=f"Updated entity {request.entity_id}",
        data=result
    )

@router.post("/remove_entity", operation_id="remove_entity", summary="Remove entity from registry")
async def remove_entity(request: RemoveEntityRequest = Body(...)):
    """Remove an entity from the Home Assistant entity registry.

    First attempts registry-level removal via the WebSocket API. If the entity
    is not in the registry (e.g. it is a YAML-defined or state-only entity),
    falls back to state-level deletion via the REST API so the caller does not
    get a 500 for a legitimate entity that simply isn't registry-managed.
    """
    ws = await get_ws_client()

    # Step 1: Try entity registry removal
    try:
        result = await ws.call_command(
            "config/entity_registry/remove",
            entity_id=request.entity_id
        )
        return SuccessResponse(
            message=f"Removed entity {request.entity_id} from registry",
            data=result
        )
    except Exception as e:
        error_msg = str(e)
        logger.warning(f"Registry removal failed for {request.entity_id}: {error_msg}")

        # If the error is NOT "Entity not found", re-raise as 500
        if "not found" not in error_msg.lower():
            logger.error(f"Unexpected registry error for {request.entity_id}: {error_msg}", exc_info=True)
            raise HTTPException(status_code=500, detail=error_msg)

    # Step 2: Entity not in registry — check if it exists in the state machine
    try:
        state = await ha_api.get_states(request.entity_id)
    except Exception as e:
        logger.error(f"Failed to check state for {request.entity_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Entity not in registry and state lookup failed: {e}"
        )

    if not state:
        raise HTTPException(
            status_code=404,
            detail=f"Entity {request.entity_id} not found in registry or state machine"
        )

    # Step 3: Entity exists in state machine but not registry — delete via REST API
    try:
        await ha_api.call_api("DELETE", f"/states/{request.entity_id}")
        return SuccessResponse(
            message=f"Entity {request.entity_id} was not in the registry; removed from state machine",
            data={"entity_id": request.entity_id, "registry": False, "state_removed": True}
        )
    except Exception as e:
        logger.error(f"State removal failed for {request.entity_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Entity not in registry and state removal failed: {e}"
        )

@router.post("/get_entity_exposure", operation_id="get_entity_exposure", summary="Get entity exposure settings")
async def get_entity_exposure(request: GetEntityExposureRequest = Body(...)):
    """Get entity exposure settings for cloud/voice assistants."""
    try:
        # Read exposed entities from storage
        from pathlib import Path
        from app.core.config import settings
        import aiofiles
        
        exposed_file = Path(settings.HA_CONFIG_PATH) / ".storage" / "homeassistant.exposed_entities"
        
        if not exposed_file.exists():
            return SuccessResponse(
                message="No exposure settings found",
                data={}
            )
        
        async with aiofiles.open(exposed_file, 'r') as f:
            content = await f.read()
            import json as _json
            data = _json.loads(content)
        
        entities = data.get("data", {}).get("entities", {})
        
        if request.entity_id:
            entity_data = entities.get(request.entity_id)
            if not entity_data:
                raise HTTPException(status_code=404, detail=f"No exposure settings for {request.entity_id}")
            return SuccessResponse(
                message=f"Exposure settings for {request.entity_id}",
                data={request.entity_id: entity_data}
            )
        
        return SuccessResponse(
            message=f"Found exposure settings for {len(entities)} entities",
            data=entities
        )
    
    except Exception as e:
        logger.error(f"Error getting entity exposure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
