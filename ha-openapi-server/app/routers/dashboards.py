"""Lovelace dashboard management: list, config, card creation with dry-run."""
import logging
import yaml
from typing import Any, Dict, Optional
from fastapi import APIRouter, Body, HTTPException
from app.core.clients import get_ws_client
from app.models.common import SuccessResponse
from app.models.dashboard import (
    GetDashboardConfigRequest,
    UpdateDashboardConfigRequest,
    ListDashboardsRequest,
    CreateDashboardRequest,
    DeleteDashboardRequest,
    ManualCreateCustomCardRequest,
    ManualEditCustomCardRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["dashboards"])


@router.post("/list_dashboards", operation_id="list_dashboards", summary="List all Lovelace dashboards")
async def ha_list_dashboards(request: ListDashboardsRequest = Body(default_factory=ListDashboardsRequest)):
    """List all Lovelace dashboards via WebSocket.
    Returns the default dashboard (lovelace) plus any custom dashboards.
    """
    ws = await get_ws_client()
    try:
        dashboards = await ws.call_command("lovelace/dashboards/list")
        # dashboards is a list of dicts with: id, url_path, title, icon, require_admin, show_in_sidebar, mode
        result = []
        for d in dashboards:
            result.append({
                "id": d.get("id"),
                "url_path": d.get("url_path"),
                "title": d.get("title"),
                "icon": d.get("icon"),
                "require_admin": d.get("require_admin", False),
                "show_in_sidebar": d.get("show_in_sidebar", False),
                "mode": d.get("mode", "storage"),
            })
        # Always include default dashboard
        result.insert(0, {"id": "lovelace", "url_path": "lovelace", "title": "Default Dashboard", "icon": None, "require_admin": False, "show_in_sidebar": True, "mode": "storage"})
        return SuccessResponse(message=f"Found {len(result)} dashboards", data=result)
    except Exception as e:
        logger.error(f"Error listing dashboards: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get_dashboard_config", operation_id="get_dashboard_config", summary="Get dashboard config")
async def ha_get_dashboard_config(request: GetDashboardConfigRequest = Body(...)):
    """Get Lovelace dashboard configuration via WebSocket."""
    ws = await get_ws_client()
    url_path = request.dashboard_id if request.dashboard_id != "lovelace" else None
    
    if url_path:
        config = await ws.call_command("lovelace/config", url_path=url_path)
    else:
        config = await ws.call_command("lovelace/config")
        
    return SuccessResponse(message="Dashboard config retrieved", data=config)


@router.post("/save_dashboard_config", operation_id="save_dashboard_config", summary="Save dashboard config")
async def ha_save_dashboard_config(request: UpdateDashboardConfigRequest = Body(...)):
    """Save full Lovelace dashboard configuration via WebSocket."""
    ws = await get_ws_client()
    url_path = request.dashboard_id if request.dashboard_id != "lovelace" else None

    try:
        if url_path:
            result = await ws.call_command("lovelace/config/save", url_path=url_path, config=request.config)
        else:
            result = await ws.call_command("lovelace/config/save", config=request.config)
        return SuccessResponse(message="Dashboard config saved", data=result)
    except Exception as e:
        logger.error(f"Error saving dashboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/manual_create_custom_card", operation_id="manual_create_custom_card", summary="Create custom card with dry-run support")
async def ha_manual_create_custom_card(request: ManualCreateCustomCardRequest = Body(...)):
    """Create a custom card on a Lovelace dashboard.

    Set dry_run=true to preview the card without saving. The response includes:
    - parsed_card: the parsed YAML as a dict (for validation)
    - preview_config: the full dashboard config with the card inserted (for visual check)
    - applied: false if dry_run, true if saved

    The card is inserted at the specified position (default: append to end of view).
    """
    # Parse YAML first — catch syntax errors before doing anything
    try:
        card_config = yaml.safe_load(request.card_yaml)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"YAML parse error: {e}")

    if not isinstance(card_config, dict):
        raise HTTPException(status_code=400, detail="Card YAML must be a dict/object with a 'type' key")
    if "type" not in card_config:
        raise HTTPException(status_code=400, detail="Card YAML must include a 'type' key")

    ws = await get_ws_client()
    url_path = request.dashboard_id if request.dashboard_id != "lovelace" else None

    # Get current dashboard config
    if url_path:
        config = await ws.call_command("lovelace/config", url_path=url_path)
    else:
        config = await ws.call_command("lovelace/config")

    # Validate view_index exists
    views = config.get("views", [])
    if request.view_index < 0 or request.view_index >= len(views):
        raise HTTPException(status_code=400, detail=f"View index {request.view_index} out of range (0-{len(views)-1})")

    # Deep copy config for preview/apply
    import copy
    new_config = copy.deepcopy(config)
    view = new_config["views"][request.view_index]

    # Ensure cards list exists
    if "cards" not in view:
        view["cards"] = []

    # Insert card at position or append
    pos = request.position if request.position is not None else len(view["cards"])
    pos = max(0, min(pos, len(view["cards"])))
    view["cards"].insert(pos, card_config)

    # Check if this is a dry run (check for dry_run field in request)
    # ManualCreateCustomCardRequest doesn't have dry_run, so we check if position is -1
    # Actually, let's add dry_run support properly
    dry_run = getattr(request, "dry_run", False)

    if dry_run:
        return SuccessResponse(
            message="Dry run — card not saved",
            data={
                "applied": False,
                "parsed_card": card_config,
                "preview_config": new_config,
                "view_index": request.view_index,
                "card_position": pos,
                "view_title": view.get("title", view.get("path", f"view_{request.view_index}")),
                "total_cards_in_view": len(view["cards"]),
            }
        )

    # Apply: save the modified config
    try:
        if url_path:
            result = await ws.call_command("lovelace/config/save", url_path=url_path, config=new_config)
        else:
            result = await ws.call_command("lovelace/config/save", config=new_config)
        return SuccessResponse(
            message="Card created and saved",
            data={
                "applied": True,
                "parsed_card": card_config,
                "view_index": request.view_index,
                "card_position": pos,
                "view_title": view.get("title", view.get("path", f"view_{request.view_index}")),
                "total_cards_in_view": len(view["cards"]),
                "save_result": result,
            }
        )
    except Exception as e:
        logger.error(f"Error saving card: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Save failed: {e}")


@router.post("/manual_edit_custom_card", operation_id="manual_edit_custom_card", summary="Edit existing card")
async def ha_manual_edit_custom_card(request: ManualEditCustomCardRequest = Body(...)):
    """Edit an existing card on a Lovelace dashboard."""
    try:
        card_config = yaml.safe_load(request.card_yaml)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"YAML parse error: {e}")

    if not isinstance(card_config, dict):
        raise HTTPException(status_code=400, detail="Card YAML must be a dict/object")

    ws = await get_ws_client()
    url_path = request.dashboard_id if request.dashboard_id != "lovelace" else None

    if url_path:
        config = await ws.call_command("lovelace/config", url_path=url_path)
    else:
        config = await ws.call_command("lovelace/config")

    import copy
    new_config = copy.deepcopy(config)
    view = new_config["views"][request.view_index]
    cards = view.get("cards", [])

    if request.card_index < 0 or request.card_index >= len(cards):
        raise HTTPException(status_code=400, detail=f"Card index {request.card_index} out of range (0-{len(cards)-1})")

    cards[request.card_index] = card_config

    try:
        if url_path:
            result = await ws.call_command("lovelace/config/save", url_path=url_path, config=new_config)
        else:
            result = await ws.call_command("lovelace/config/save", config=new_config)
        return SuccessResponse(message="Card updated and saved", data={"applied": True, "card": card_config})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save failed: {e}")


@router.post("/list_dashboard_views", operation_id="list_dashboard_views", summary="List views in a dashboard")
async def ha_list_dashboard_views(request: GetDashboardConfigRequest = Body(...)):
    """List all views/tabs in a dashboard with their titles and card counts."""
    ws = await get_ws_client()
    url_path = request.dashboard_id if request.dashboard_id != "lovelace" else None

    if url_path:
        config = await ws.call_command("lovelace/config", url_path=url_path)
    else:
        config = await ws.call_command("lovelace/config")

    views = config.get("views", [])
    result = []
    for i, v in enumerate(views):
        result.append({
            "index": i,
            "title": v.get("title", v.get("path", f"view_{i}")),
            "path": v.get("path", f"view_{i}"),
            "icon": v.get("icon"),
            "card_count": len(v.get("cards", [])),
        })
    return SuccessResponse(message=f"Found {len(result)} views", data=result)


@router.post("/preview_card", operation_id="preview_card", summary="Preview card without saving (dry run)")
async def ha_preview_card(request: ManualCreateCustomCardRequest = Body(...)):
    """Preview a card on a dashboard without saving. Returns the full config
    with the card inserted so you can verify before applying.

    This is the same as manual_create_custom_card but always dry_run=true.
    """
    try:
        card_config = yaml.safe_load(request.card_yaml)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"YAML parse error: {e}")

    if not isinstance(card_config, dict):
        raise HTTPException(status_code=400, detail="Card YAML must be a dict/object with a 'type' key")
    if "type" not in card_config:
        raise HTTPException(status_code=400, detail="Card YAML must include a 'type' key")

    ws = await get_ws_client()
    url_path = request.dashboard_id if request.dashboard_id != "lovelace" else None

    if url_path:
        config = await ws.call_command("lovelace/config", url_path=url_path)
    else:
        config = await ws.call_command("lovelace/config")

    views = config.get("views", [])
    if request.view_index < 0 or request.view_index >= len(views):
        raise HTTPException(status_code=400, detail=f"View index {request.view_index} out of range (0-{len(views)-1})")

    import copy
    new_config = copy.deepcopy(config)
    view = new_config["views"][request.view_index]

    if "cards" not in view:
        view["cards"] = []

    pos = request.position if request.position is not None else len(view["cards"])
    pos = max(0, min(pos, len(view["cards"])))
    view["cards"].insert(pos, card_config)

    return SuccessResponse(
        message="Preview generated — card NOT saved",
        data={
            "applied": False,
            "parsed_card": card_config,
            "view_index": request.view_index,
            "card_position": pos,
            "view_title": view.get("title", view.get("path", f"view_{request.view_index}")),
            "total_cards_in_view": len(view["cards"]),
            "card_types_in_view": [c.get("type", "?") for c in view["cards"]],
        }
    )