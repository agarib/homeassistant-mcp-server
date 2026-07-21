import logging
import aiofiles
import yaml
from fastapi import APIRouter, Body, HTTPException
from app.core.clients import ha_api
from app.core.config import settings
from app.models.common import SuccessResponse
from app.models.automation import (
    ListAutomationsRequest, TriggerAutomationRequest,
    CreateAutomationRequest, UpdateAutomationRequest,
    DeleteAutomationRequest, ToggleAutomationRequest,
    ReloadAutomationsRequest, GetAutomationDetailsRequest,
    CreateSceneRequest, ActivateSceneRequest, ListScenesRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["automations"])

@router.post("/list_automations", operation_id="list_automations", summary="List automations")
async def ha_list_automations(request: ListAutomationsRequest = Body(...)):
    """List configured automations."""
    states = await ha_api.get_states()
    automations = [
        {"entity_id": s["entity_id"], "alias": s["attributes"].get("friendly_name"), "state": s["state"]}
        for s in states if s["entity_id"].startswith("automation.")
    ]
    
    if request.enabled_only:
        automations = [a for a in automations if a["state"] == "on"]
        
    return SuccessResponse(message=f"Found {len(automations)} automations", data=automations)

@router.post("/trigger_automation", operation_id="trigger_automation", summary="Trigger an automation")
async def ha_trigger_automation(request: TriggerAutomationRequest = Body(...)):
    """Trigger an automation."""
    result = await ha_api.call_service(
        "automation", "trigger", 
        entity_id=request.automation_id, 
        skip_condition=request.skip_condition
    )
    return SuccessResponse(message=f"Triggered {request.automation_id}", data=result)

@router.post("/toggle_automation", operation_id="toggle_automation", summary="Enable or disable an automation")
async def ha_toggle_automation(request: ToggleAutomationRequest = Body(...)):
    """Enable or disable an automation."""
    service = "turn_on" if request.enable else "turn_off"
    await ha_api.call_service("automation", service, entity_id=request.automation_id)
    status = "enabled" if request.enable else "disabled"
    return SuccessResponse(message=f"Automation {request.automation_id} {status}")

@router.post("/get_automation_details", operation_id="get_automation_details", summary="Get automation details")
async def ha_get_automation_details(request: GetAutomationDetailsRequest = Body(...)):
    """Get detailed information about a specific automation."""
    state = await ha_api.get_states(request.automation_id)
    
    if not state:
        raise HTTPException(status_code=404, detail=f"Automation {request.automation_id} not found")
    
    return SuccessResponse(
        message=f"Retrieved details for {request.automation_id}",
        data={
            "entity_id": state.get("entity_id"),
            "alias": state.get("attributes", {}).get("friendly_name"),
            "state": state.get("state"),
            "last_triggered": state.get("attributes", {}).get("last_triggered"),
            "mode": state.get("attributes", {}).get("mode"),
            "current": state.get("attributes", {}).get("current", 0),
            "max": state.get("attributes", {}).get("max")
        }
    )

@router.post("/reload_automations", operation_id="reload_automations", summary="Reload automations")
async def ha_reload_automations(request: ReloadAutomationsRequest = Body(...)):
    """Reload automations from YAML configuration."""
    if request.validate_only:
        # Note: In a real implementation this might check config first
        # For refactoring parity, assuming basic pass if valid YAML structure, 
        # basically a no-op until validation logic is moved here or call_service used
        pass

    await ha_api.call_service("automation", "reload")
    return SuccessResponse(message="Automations reloaded successfully")

@router.post("/create_automation", operation_id="create_automation", summary="Create a new automation")
async def ha_create_automation(request: CreateAutomationRequest = Body(...)):
    """
    Create sophisticated automation with triggers, conditions, and actions.
    """
    try:
        # Build automation config
        automation_config = {
            "alias": request.alias,
            "trigger": request.trigger,
            "action": request.action,
            "mode": request.mode
        }
        
        if request.condition:
            automation_config["condition"] = request.condition
        
        # Write to automations.yaml
        automations_file = settings.HA_CONFIG_PATH / "automations.yaml"
        
        # Read existing automations
        if automations_file.exists():
            async with aiofiles.open(automations_file, 'r') as f:
                content = await f.read()
                existing = yaml.safe_load(content) or []
        else:
            existing = []
        
        # Add new automation
        existing.append(automation_config)
        
        # Write back
        async with aiofiles.open(automations_file, 'w') as f:
            await f.write(yaml.dump(existing, default_flow_style=False))
        
        # Reload automations
        await ha_api.call_service("automation", "reload")
        
        return SuccessResponse(
            message=f"Automation '{request.alias}' created successfully",
            data=automation_config
        )
        
    except Exception as e:
        logger.error(f"Error creating automation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_automation", operation_id="update_automation", summary="Update an existing automation")
async def ha_update_automation(request: UpdateAutomationRequest = Body(...)):
    """Update existing automation."""
    try:
        automations_file = settings.HA_CONFIG_PATH / "automations.yaml"
        
        if not automations_file.exists():
            raise HTTPException(status_code=404, detail="No automations.yaml found")
        
        # Read existing automations
        async with aiofiles.open(automations_file, 'r') as f:
            content = await f.read()
            automations = yaml.safe_load(content) or []
        
        # Find and update the automation
        automation_name = request.automation_id.replace("automation.", "")
        
        import re as _re
        def normalize(s):
            result = ''.join(c if c.isalnum() else '_' for c in s.lower())
            return _re.sub(r'_+', '_', result)  # collapse consecutive underscores
        
        found = False
        for auto in automations:
            alias_normalized = normalize(auto.get('alias', ''))
            # Try matching by id first, then by normalized alias
            if (auto.get('id') == automation_name or 
                alias_normalized == normalize(automation_name)):
                found = True
                found = True
                if request.alias:
                    auto['alias'] = request.alias
                if request.trigger:
                    auto['trigger'] = request.trigger
                if request.condition is not None:
                    auto['condition'] = request.condition
                if request.action:
                    auto['action'] = request.action
                if request.mode:
                    auto['mode'] = request.mode
                break
        
        if not found:
            # Also search packages directory for YAML-managed automations
            import yaml as _yaml
            from pathlib import Path as _Path
            pkgs_dir = _Path(settings.HA_CONFIG_PATH) / "packages"
            found_in_pkg = False
            if pkgs_dir.exists():
                for pkg_dir in pkgs_dir.iterdir():
                    if pkg_dir.is_dir() and not found_in_pkg:
                        for yf in pkg_dir.glob("*.yaml"):
                            async with aiofiles.open(yf, 'r') as f:
                                pkg_content = await f.read()
                            pkg = _yaml.safe_load(pkg_content) or {}
                            if isinstance(pkg, dict) and "automation" in pkg:
                                for pa in pkg["automation"]:
                                    if (pa.get('id') == automation_name or 
                                        normalize(pa.get('alias', '')) == normalize(automation_name)):
                                        found_in_pkg = True
                                        auto = pa
                                        current_file = yf
                                        break
                            if found_in_pkg:
                                break
                    if found_in_pkg:
                        break
            
            if found_in_pkg:
                # Update in place
                if request.alias:
                    auto['alias'] = request.alias
                if request.trigger:
                    auto['trigger'] = request.trigger
                if request.condition is not None:
                    auto['condition'] = request.condition
                if request.action:
                    auto['action'] = request.action
                if request.mode:
                    auto['mode'] = request.mode
                
                # Save back to package file
                async with aiofiles.open(current_file, 'w') as f:
                    await f.write(yaml.dump(pkg, default_flow_style=False))
                await ha_api.call_service("automation", "reload")
                return SuccessResponse(message=f"Automation {request.automation_id} updated (package)")
            
            raise HTTPException(status_code=404, detail=f"Automation {request.automation_id} not found")
        
        # Write back
        async with aiofiles.open(automations_file, 'w') as f:
            await f.write(yaml.dump(automations, default_flow_style=False))
        
        # Reload automations
        await ha_api.call_service("automation", "reload")
        
        return SuccessResponse(
            message=f"Automation {request.automation_id} updated successfully"
        )
    except Exception as e:
        logger.error(f"Error updating automation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_automation", operation_id="delete_automation", summary="Delete an automation")
async def ha_delete_automation(request: DeleteAutomationRequest = Body(...)):
    """Delete automation from Home Assistant."""
    try:
        if not request.confirm:
            raise HTTPException(status_code=400, detail="Must set confirm=true to delete automation")
        
        automations_file = settings.HA_CONFIG_PATH / "automations.yaml"
        
        if not automations_file.exists():
            raise HTTPException(status_code=404, detail="No automations.yaml found")
        
        # Read existing automations
        async with aiofiles.open(automations_file, 'r') as f:
            content = await f.read()
            automations = yaml.safe_load(content) or []
        
        # Find and remove the automation
        automation_name = request.automation_id.replace("automation.", "")
        
        import re as _re
        def normalize(s):
            result = ''.join(c if c.isalnum() else '_' for c in s.lower())
            return _re.sub(r'_+', '_', result)  # collapse consecutive underscores
        
        original_count = len(automations)
        automations = [
            auto for auto in automations
            if (auto.get('id') != automation_name and 
                normalize(auto.get('alias', '')) != normalize(automation_name))
        ]
        
        if len(automations) == original_count:
            raise HTTPException(status_code=404, detail=f"Automation {request.automation_id} not found")
        
        # Write back
        async with aiofiles.open(automations_file, 'w') as f:
            await f.write(yaml.dump(automations, default_flow_style=False))
        
        # Reload automations
        await ha_api.call_service("automation", "reload")
        
        return SuccessResponse(message=f"Automation {request.automation_id} deleted successfully")
        
    except Exception as e:
        logger.error(f"Error deleting automation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_scene", operation_id="create_scene", summary="Create a scene")
async def ha_create_scene(request: CreateSceneRequest = Body(...)):
    """Create a temporary scene."""
    await ha_api.call_service(
        "scene", "create",
        scene_id=request.scene_id.replace("scene.", ""), # service expects name, not entity_id sometimes, or full ID
        entities=request.entities,
        snapshot_entities=list(request.entities.keys())
    )
    return SuccessResponse(message=f"Created scene {request.scene_id}")

@router.post("/activate_scene", operation_id="activate_scene", summary="Activate a scene")
async def ha_activate_scene(request: ActivateSceneRequest = Body(...)):
    """Activate a scene."""
    await ha_api.call_service("scene", "turn_on", entity_id=request.scene_id)
    return SuccessResponse(message=f"Activated scene {request.scene_id}")

@router.post("/list_scenes", operation_id="list_scenes", summary="List all scenes")
async def ha_list_scenes(request: ListScenesRequest = Body(...)):
    """List all configured scenes."""
    states = await ha_api.get_states()
    scenes = [
        {
            "entity_id": s["entity_id"], 
            "name": s["attributes"].get("friendly_name", s["entity_id"].replace("scene.", "")),
            "icon": s["attributes"].get("icon")
        }
        for s in states if s["entity_id"].startswith("scene.")
    ]
    return SuccessResponse(message=f"Found {len(scenes)} scenes", data=scenes)
