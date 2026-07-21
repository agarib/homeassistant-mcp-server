import logging
import yaml
import aiofiles
from fastapi import APIRouter, Body, HTTPException
from app.core.clients import ha_api
from app.core.config import settings
from app.models.common import SuccessResponse
from app.models.scripts import (
    GetScriptRequest, SetScriptRequest, RemoveScriptRequest
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["scripts"])

@router.post("/config_get_script", operation_id="config_get_script", summary="Get Home Assistant script configuration")
async def config_get_script(request: GetScriptRequest = Body(...)):
    """Retrieve script configuration from scripts.yaml or packages."""
    from pathlib import Path
    
    script_id = request.script_id
    if not script_id.startswith("script."):
        script_id = f"script.{script_id}"
    script_name = script_id.replace("script.", "")
    
    # Check scripts.yaml first
    scripts_file = Path(settings.HA_CONFIG_PATH) / "scripts.yaml"
    if scripts_file.exists():
        async with aiofiles.open(scripts_file, 'r') as f:
            content = await f.read()
            scripts = yaml.safe_load(content) or {}
            if isinstance(scripts, dict) and script_name in scripts:
                return SuccessResponse(
                    message=f"Retrieved script {script_id}",
                    data={script_name: scripts[script_name]}
                )
    
    # Check packages directory
    packages_dir = Path(settings.HA_CONFIG_PATH) / "packages"
    if packages_dir.exists():
        for pkg_dir in packages_dir.iterdir():
            if pkg_dir.is_dir():
                for yaml_file in pkg_dir.glob("*.yaml"):
                    async with aiofiles.open(yaml_file, 'r') as f:
                        content = await f.read()
                    pkg = yaml.safe_load(content) or {}
                    if isinstance(pkg, dict) and "script" in pkg:
                        scripts_in_pkg = pkg["script"]
                        if isinstance(scripts_in_pkg, dict) and script_name in scripts_in_pkg:
                            return SuccessResponse(
                                message=f"Retrieved script {script_id} from {yaml_file.name}",
                                data={script_name: scripts_in_pkg[script_name]}
                            )
    
    raise HTTPException(status_code=404, detail=f"Script {script_id} not found")

@router.post("/config_set_script", operation_id="config_set_script", summary="Create or update a Home Assistant script")
async def config_set_script(request: SetScriptRequest = Body(...)):
    """Create or update a script in scripts.yaml."""
    from pathlib import Path
    import aiofiles
    
    script_id = request.script_id
    if not script_id.startswith("script."):
        script_id = f"script.{script_id}"
    script_name = script_id.replace("script.", "")
    
    scripts_file = Path(settings.HA_CONFIG_PATH) / "scripts.yaml"
    
    # Read existing or create new
    if scripts_file.exists():
        async with aiofiles.open(scripts_file, 'r') as f:
            content = await f.read()
        scripts = yaml.safe_load(content) or {}
    else:
        scripts = {}
    
    if not isinstance(scripts, dict):
        scripts = {}
    
    # Build script config
    script_config = {}
    if request.alias:
        script_config["alias"] = request.alias
    if request.sequence:
        script_config["sequence"] = request.sequence
    if request.description:
        script_config["description"] = request.description
    if request.mode:
        script_config["mode"] = request.mode
    if request.icon:
        script_config["icon"] = request.icon
    if request.fields:
        script_config["fields"] = request.fields
    
    scripts[script_name] = script_config
    
    # Write back
    async with aiofiles.open(scripts_file, 'w') as f:
        await f.write(yaml.dump(scripts, default_flow_style=False, allow_unicode=True))
    
    # Reload scripts
    await ha_api.call_service("script", "reload")
    
    return SuccessResponse(
        message=f"{'Updated' if script_name in scripts else 'Created'} script {script_id}",
        data=script_config
    )

@router.post("/config_remove_script", operation_id="config_remove_script", summary="Delete a Home Assistant script")
async def config_remove_script(request: RemoveScriptRequest = Body(...)):
    """Delete a script from scripts.yaml."""
    from pathlib import Path
    
    if not request.confirm:
        raise HTTPException(status_code=400, detail="Must set confirm=true to delete script")
    
    script_id = request.script_id
    if not script_id.startswith("script."):
        script_id = f"script.{script_id}"
    script_name = script_id.replace("script.", "")
    
    scripts_file = Path(settings.HA_CONFIG_PATH) / "scripts.yaml"
    
    if not scripts_file.exists():
        raise HTTPException(status_code=404, detail="scripts.yaml not found")
    
    async with aiofiles.open(scripts_file, 'r') as f:
        content = await f.read()
    scripts = yaml.safe_load(content) or {}
    
    if not isinstance(scripts, dict) or script_name not in scripts:
        raise HTTPException(status_code=404, detail=f"Script {script_id} not found")
    
    del scripts[script_name]
    
    async with aiofiles.open(scripts_file, 'w') as f:
        await f.write(yaml.dump(scripts, default_flow_style=False, allow_unicode=True))
    
    await ha_api.call_service("script", "reload")
    
    return SuccessResponse(message=f"Deleted script {script_id}")
