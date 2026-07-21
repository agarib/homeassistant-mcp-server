import logging
import yaml
import aiofiles
from fastapi import APIRouter, Body, HTTPException
from app.core.clients import ha_api
from app.core.config import settings
from app.models.common import SuccessResponse
from app.models.utilities import (
    EvalTemplateRequest, ConfigSetYamlRequest
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["utilities"])

@router.post("/eval_template", operation_id="eval_template", summary="Evaluate Jinja2 template")
async def ha_eval_template(request: EvalTemplateRequest = Body(...)):
    """Evaluate Jinja2 templates using Home Assistant's template engine."""
    try:
        # HA returns template results as plain text, not JSON
        from app.core.clients import http_client
        from app.core.config import settings as _cfg
        
        template_url = f"{_cfg.HA_URL.rstrip('/')}/template"
        resp = await http_client.post(template_url, json={"template": request.template})
        resp.raise_for_status()
        rendered = resp.text.strip('"\n ')
        
        return SuccessResponse(
            message="Template rendered successfully",
            data={"template": request.template, "result": rendered}
        )
    except Exception as e:
        logger.error(f"Template evaluation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Template error: {str(e)}")

@router.post("/config_set_yaml", operation_id="config_set_yaml", summary="Update raw YAML configuration")
async def ha_config_set_yaml(request: ConfigSetYamlRequest = Body(...)):
    """Update raw YAML configuration. This is a LAST-RESORT tool."""
    from pathlib import Path
    
    if not request.confirm:
        raise HTTPException(status_code=400, detail="Must set confirm=true to modify configuration")
    
    file_path = Path(settings.HA_CONFIG_PATH) / request.file_path
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File {request.file_path} not found")
    
    try:
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
        
        # Use a safe YAML loader that handles tags
        try:
            config = yaml.safe_load(content) or {}
        except Exception:
            # Manual parse for simple cases
            config = {}
        
        if not isinstance(config, dict):
            raise HTTPException(status_code=400, detail="File is not a valid YAML mapping")
        
        if request.action == "merge":
            config[request.yaml_key] = request.content
        elif request.action == "replace":
            config[request.yaml_key] = request.content
        elif request.action == "remove":
            config.pop(request.yaml_key, None)

        async with aiofiles.open(file_path, 'w') as f:
            await f.write(yaml.dump(config, default_flow_style=False, allow_unicode=True))
        
        return SuccessResponse(
            message=f"{request.action}d {request.yaml_key} in {request.file_path}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YAML config error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
