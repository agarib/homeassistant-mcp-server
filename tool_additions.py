# Home Assistant OpenAPI Server - Tool Additions
# Add these to server.py after the existing endpoints

"""
This file adds:
- 12 Native MCPO HA tools (converted to FastAPI/Pydantic)
- 4 New System Logging tools
Total: 16 new tools → 93 tools total (77 existing + 16 new)
"""

# ============================================================================
# NATIVE HOME ASSISTANT MCP TOOLS (12 tools from MCPO)
# ============================================================================

# 1. Control Light
class ControlLightRequest(BaseModel):
    entity_id: str = Field(..., description="Light entity ID (e.g., 'light.living_room')")
    action: str = Field(..., description="Action: 'turn_on', 'turn_off', 'toggle', 'brightness', 'color'")
    brightness: Optional[int] = Field(None, ge=0, le=255, description="Brightness (0-255)")
    rgb_color: Optional[List[int]] = Field(None, description="RGB color [R, G, B] (0-255 each)")
    color_temp: Optional[int] = Field(None, description="Color temperature in mireds")

@app.post("/control_light", summary="Control lights", tags=["native_mcpo"])
async def control_light(request: ControlLightRequest = Body(...)):
    """
    Control lights with full support for brightness, color, and temperature.
    
    **ACTIONS:**
    - `turn_on` - Turn light on
    - `turn_off` - Turn light off
    - `toggle` - Toggle state
    - `brightness` - Set brightness (requires brightness parameter)
    - `color` - Set RGB color (requires rgb_color parameter)
    
    Example: {
        "entity_id": "light.living_room",
        "action": "turn_on",
        "brightness": 200,
        "rgb_color": [255, 200, 100]
    }
    """
    try:
        service_data = {}
        
        if request.action == "turn_on":
            service = "turn_on"
            if request.brightness is not None:
                service_data["brightness"] = request.brightness
            if request.rgb_color is not None:
                service_data["rgb_color"] = request.rgb_color
            if request.color_temp is not None:
                service_data["color_temp"] = request.color_temp
        elif request.action == "turn_off":
            service = "turn_off"
        elif request.action == "toggle":
            service = "toggle"
        elif request.action == "brightness":
            service = "turn_on"
            service_data["brightness"] = request.brightness
        elif request.action == "color":
            service = "turn_on"
            service_data["rgb_color"] = request.rgb_color
        else:
            raise HTTPException(status_code=400, detail=f"Invalid action: {request.action}")
        
        result = await ha_api.call_service("light", service, request.entity_id, **service_data)
        
        return SuccessResponse(
            message=f"Light {request.action} successful",
            data={"entity_id": request.entity_id, "action": request.action, **service_data}
        )
    except Exception as e:
        logger.error(f"Error controlling light: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 2. Control Switch
class ControlSwitchRequest(BaseModel):
    entity_id: str = Field(..., description="Switch entity ID")
    action: str = Field(..., description="Action: 'turn_on', 'turn_off', 'toggle'")

@app.post("/control_switch", summary="Control switches", tags=["native_mcpo"])
async def control_switch(request: ControlSwitchRequest = Body(...)):
    """Control switches (turn on/off/toggle)"""
    try:
        result = await ha_api.call_service("switch", request.action, request.entity_id)
        return SuccessResponse(
            message=f"Switch {request.action} successful",
            data={"entity_id": request.entity_id, "action": request.action}
        )
    except Exception as e:
        logger.error(f"Error controlling switch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 3. Get Entity State
class GetEntityStateRequest(BaseModel):
    entity_id: str = Field(..., description="Entity ID to query")

@app.post("/get_entity_state", summary="Get entity state", tags=["native_mcpo"])
async def get_entity_state(request: GetEntityStateRequest = Body(...)):
    """Get current state and attributes of any entity"""
    try:
        state = await ha_api.get_states(request.entity_id)
        return SuccessResponse(
            message=f"State for {request.entity_id}",
            data=state
        )
    except Exception as e:
        logger.error(f"Error getting entity state: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 4. List Entities
class ListEntitiesRequest(BaseModel):
    domain: Optional[str] = Field(None, description="Filter by domain (e.g., 'light', 'switch')")

@app.post("/list_entities", summary="List all entities", tags=["native_mcpo"])
async def list_entities(request: ListEntitiesRequest = Body(...)):
    """List all Home Assistant entities, optionally filtered by domain"""
    try:
        states = await ha_api.get_states()
        
        if request.domain:
            states = [s for s in states if s["entity_id"].startswith(f"{request.domain}.")]
        
        entity_list = [
            {
                "entity_id": s["entity_id"],
                "state": s["state"],
                "friendly_name": s.get("attributes", {}).get("friendly_name", s["entity_id"])
            }
            for s in states
        ]
        
        return SuccessResponse(
            message=f"Found {len(entity_list)} entities" + (f" in domain '{request.domain}'" if request.domain else ""),
            data={"entities": entity_list, "count": len(entity_list)}
        )
    except Exception as e:
        logger.error(f"Error listing entities: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 5. Call Service (Generic)
class CallServiceRequest(BaseModel):
    domain: str = Field(..., description="Service domain (e.g., 'light', 'switch')")
    service: str = Field(..., description="Service name (e.g., 'turn_on')")
    entity_id: Optional[str] = Field(None, description="Entity ID (optional)")
    service_data: Optional[Dict[str, Any]] = Field(None, description="Additional service data")

@app.post("/call_service", summary="Call any Home Assistant service", tags=["native_mcpo"])
async def call_service(request: CallServiceRequest = Body(...)):
    """
    Call any Home Assistant service with optional data.
    
    Example: {
        "domain": "climate",
        "service": "set_temperature",
        "entity_id": "climate.living_room",
        "service_data": {"temperature": 22}
    }
    """
    try:
        service_data = request.service_data or {}
        result = await ha_api.call_service(
            request.domain,
            request.service,
            request.entity_id,
            **service_data
        )
        
        return SuccessResponse(
            message=f"Service {request.domain}.{request.service} called",
            data={"domain": request.domain, "service": request.service, "entity_id": request.entity_id}
        )
    except Exception as e:
        logger.error(f"Error calling service: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 6. Get Services
@app.post("/get_services", summary="List available services", tags=["native_mcpo"])
async def get_services():
    """Get all available Home Assistant services"""
    try:
        services = await ha_api.get_services()
        return SuccessResponse(
            message="Available services retrieved",
            data=services
        )
    except Exception as e:
        logger.error(f"Error getting services: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 7. Fire Event
class FireEventRequest(BaseModel):
    event_type: str = Field(..., description="Event type to fire")
    event_data: Optional[Dict[str, Any]] = Field(None, description="Event data payload")

@app.post("/fire_event", summary="Fire custom event", tags=["native_mcpo"])
async def fire_event(request: FireEventRequest = Body(...)):
    """
    Fire a custom event in Home Assistant.
    
    Example: {
        "event_type": "my_custom_event",
        "event_data": {"message": "Hello from AI"}
    }
    """
    try:
        result = await ha_api.fire_event(request.event_type, request.event_data)
        return SuccessResponse(
            message=f"Event '{request.event_type}' fired",
            data={"event_type": request.event_type, "event_data": request.event_data}
        )
    except Exception as e:
        logger.error(f"Error firing event: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 8. Render Template
class RenderTemplateRequest(BaseModel):
    template: str = Field(..., description="Jinja2 template string")

@app.post("/render_template", summary="Render Jinja2 template", tags=["native_mcpo"])
async def render_template(request: RenderTemplateRequest = Body(...)):
    """
    Render a Jinja2 template using Home Assistant's template engine.
    
    Example: {
        "template": "{{ states('sensor.temperature') }} °C"
    }
    """
    try:
        result = await ha_api.render_template(request.template)
        return SuccessResponse(
            message="Template rendered",
            data={"template": request.template, "result": result}
        )
    except Exception as e:
        logger.error(f"Error rendering template: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 9. Get Config
@app.post("/get_config", summary="Get Home Assistant configuration", tags=["native_mcpo"])
async def get_config():
    """Get Home Assistant system configuration"""
    try:
        config = await ha_api.get_config()
        return SuccessResponse(
            message="Configuration retrieved",
            data=config
        )
    except Exception as e:
        logger.error(f"Error getting config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 10. Control Climate
class ControlClimateRequest(BaseModel):
    entity_id: str = Field(..., description="Climate entity ID")
    temperature: Optional[float] = Field(None, description="Target temperature")
    hvac_mode: Optional[str] = Field(None, description="HVAC mode: 'heat', 'cool', 'auto', 'off'")
    fan_mode: Optional[str] = Field(None, description="Fan mode")

@app.post("/control_climate", summary="Control climate devices", tags=["native_mcpo"])
async def control_climate(request: ControlClimateRequest = Body(...)):
    """Control thermostats and climate devices"""
    try:
        if request.hvac_mode:
            await ha_api.call_service(
                "climate",
                "set_hvac_mode",
                request.entity_id,
                hvac_mode=request.hvac_mode
            )
        
        if request.temperature is not None:
            await ha_api.call_service(
                "climate",
                "set_temperature",
                request.entity_id,
                temperature=request.temperature
            )
        
        if request.fan_mode:
            await ha_api.call_service(
                "climate",
                "set_fan_mode",
                request.entity_id,
                fan_mode=request.fan_mode
            )
        
        return SuccessResponse(
            message=f"Climate control successful for {request.entity_id}",
            data={
                "entity_id": request.entity_id,
                "temperature": request.temperature,
                "hvac_mode": request.hvac_mode,
                "fan_mode": request.fan_mode
            }
        )
    except Exception as e:
        logger.error(f"Error controlling climate: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 11. Get History
class GetHistoryRequest(BaseModel):
    entity_id: str = Field(..., description="Entity ID")
    start_time: Optional[str] = Field(None, description="Start time (ISO format)")
    end_time: Optional[str] = Field(None, description="End time (ISO format)")

@app.post("/get_history", summary="Get entity history", tags=["native_mcpo"])
async def get_history(request: GetHistoryRequest = Body(...)):
    """
    Get historical states for an entity.
    
    Example: {
        "entity_id": "sensor.temperature",
        "start_time": "2025-11-01T00:00:00",
        "end_time": "2025-11-01T23:59:59"
    }
    """
    try:
        # Build history URL
        url = f"{HA_URL}/api/history/period"
        if request.start_time:
            url += f"/{request.start_time}"
        
        params = {"filter_entity_id": request.entity_id}
        if request.end_time:
            params["end_time"] = request.end_time
        
        response = await http_client.get(url, params=params)
        response.raise_for_status()
        history = response.json()
        
        return SuccessResponse(
            message=f"History for {request.entity_id}",
            data={"entity_id": request.entity_id, "history": history}
        )
    except Exception as e:
        logger.error(f"Error getting history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 12. Get Logbook
class GetLogbookRequest(BaseModel):
    entity_id: Optional[str] = Field(None, description="Filter by entity ID")
    start_time: Optional[str] = Field(None, description="Start time (ISO format)")
    end_time: Optional[str] = Field(None, description="End time (ISO format)")

@app.post("/get_logbook", summary="Get logbook entries", tags=["native_mcpo"])
async def get_logbook(request: GetLogbookRequest = Body(...)):
    """
    Get Home Assistant logbook entries (state changes, events).
    
    Example: {
        "entity_id": "light.living_room",
        "start_time": "2025-11-01T00:00:00"
    }
    """
    try:
        url = f"{HA_URL}/api/logbook"
        if request.start_time:
            url += f"/{request.start_time}"
        
        params = {}
        if request.entity_id:
            params["entity"] = request.entity_id
        if request.end_time:
            params["end_time"] = request.end_time
        
        response = await http_client.get(url, params=params)
        response.raise_for_status()
        logbook = response.json()
        
        return SuccessResponse(
            message="Logbook entries retrieved",
            data={"logbook": logbook, "count": len(logbook)}
        )
    except Exception as e:
        logger.error(f"Error getting logbook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# NEW SYSTEM LOGGING & DIAGNOSTICS TOOLS (4 new tools)
# ============================================================================

# 13. Get System Logs
class GetSystemLogsRequest(BaseModel):
    lines: Optional[int] = Field(100, ge=1, le=10000, description="Number of lines to retrieve")
    level: Optional[str] = Field(None, description="Filter by log level: 'ERROR', 'WARNING', 'INFO', 'DEBUG'")

@app.post("/get_system_logs", summary="Get Home Assistant system logs", tags=["system_diagnostics"])
async def get_system_logs(request: GetSystemLogsRequest = Body(...)):
    """
    Read Home Assistant core logs to see errors, warnings, and debug info.
    
    **USE CASES:**
    - Diagnose integration failures
    - See startup errors
    - Debug automation issues
    - Monitor system health
    
    Example: {
        "lines": 100,
        "level": "ERROR"
    }
    """
    try:
        # Use Home Assistant error log API
        url = f"{HA_URL}/api/error_log"
        response = await http_client.get(url)
        response.raise_for_status()
        
        full_log = response.text
        log_lines = full_log.split('\n')
        
        # Filter by level if specified
        if request.level:
            log_lines = [line for line in log_lines if request.level.upper() in line.upper()]
        
        # Return last N lines
        log_lines = log_lines[-request.lines:]
        
        return SuccessResponse(
            message=f"Retrieved {len(log_lines)} log entries" + (f" (level: {request.level})" if request.level else ""),
            data={
                "log_lines": log_lines,
                "count": len(log_lines),
                "level_filter": request.level
            }
        )
    except Exception as e:
        logger.error(f"Error getting system logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 14. Get Persistent Notifications
@app.post("/get_persistent_notifications", summary="Get persistent notifications", tags=["system_diagnostics"])
async def get_persistent_notifications():
    """
    Get all persistent notifications (errors, warnings, updates).
    
    **SHOWS:**
    - Integration errors (like your washing machine error!)
    - Update notifications
    - Configuration warnings
    - System alerts
    
    **This is what Cloud AI was missing!**
    """
    try:
        # Get all states and filter for persistent_notification domain
        states = await ha_api.get_states()
        notifications = [
            {
                "notification_id": s["entity_id"].replace("persistent_notification.", ""),
                "title": s.get("attributes", {}).get("title", ""),
                "message": s.get("attributes", {}).get("message", ""),
                "created_at": s.get("last_changed"),
                "status": s.get("attributes", {}).get("notification_id", "")
            }
            for s in states
            if s["entity_id"].startswith("persistent_notification.")
        ]
        
        return SuccessResponse(
            message=f"Found {len(notifications)} persistent notifications",
            data={
                "notifications": notifications,
                "count": len(notifications)
            }
        )
    except Exception as e:
        logger.error(f"Error getting notifications: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 15. Get Integration Status
class GetIntegrationStatusRequest(BaseModel):
    integration: Optional[str] = Field(None, description="Specific integration to check")

@app.post("/get_integration_status", summary="Check integration health", tags=["system_diagnostics"])
async def get_integration_status(request: GetIntegrationStatusRequest = Body(...)):
    """
    Check status of Home Assistant integrations.
    
    **DETECTS:**
    - Failed integrations
    - Configuration errors
    - API connection issues
    - Update availability
    
    Example: {
        "integration": "hue"
    }
    """
    try:
        # Get config entries (integrations)
        url = f"{HA_URL}/api/config/config_entries/entry"
        response = await http_client.get(url)
        response.raise_for_status()
        
        entries = response.json()
        
        # Filter if specific integration requested
        if request.integration:
            entries = [e for e in entries if request.integration.lower() in e.get("domain", "").lower()]
        
        integration_status = [
            {
                "domain": entry.get("domain"),
                "title": entry.get("title"),
                "state": entry.get("state"),
                "entry_id": entry.get("entry_id"),
                "disabled_by": entry.get("disabled_by"),
                "supports_options": entry.get("supports_options", False)
            }
            for entry in entries
        ]
        
        return SuccessResponse(
            message=f"Found {len(integration_status)} integrations",
            data={
                "integrations": integration_status,
                "count": len(integration_status)
            }
        )
    except Exception as e:
        logger.error(f"Error getting integration status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 16. Get Startup Errors
@app.post("/get_startup_errors", summary="Get startup errors", tags=["system_diagnostics"])
async def get_startup_errors():
    """
    Get errors from last Home Assistant restart.
    
    **SHOWS:**
    - Configuration errors
    - Integration load failures
    - Component initialization issues
    - Platform setup errors
    
    **Perfect for debugging after HA restarts!**
    """
    try:
        # Get error log and parse for startup errors
        url = f"{HA_URL}/api/error_log"
        response = await http_client.get(url)
        response.raise_for_status()
        
        full_log = response.text
        log_lines = full_log.split('\n')
        
        # Look for startup-related errors (last 50 lines typically cover startup)
        startup_keywords = ['setup', 'init', 'load', 'start', 'bootstrap', 'ERROR', 'CRITICAL']
        startup_errors = []
        
        for line in log_lines[-500:]:  # Check last 500 lines
            if any(keyword in line.upper() for keyword in startup_keywords):
                if 'ERROR' in line.upper() or 'CRITICAL' in line.upper():
                    startup_errors.append(line)
        
        return SuccessResponse(
            message=f"Found {len(startup_errors)} startup-related errors",
            data={
                "startup_errors": startup_errors[-100:],  # Last 100 errors
                "count": len(startup_errors)
            }
        )
    except Exception as e:
        logger.error(f"Error getting startup errors: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Update main() to reflect new tool count
# ============================================================================

# Update the docstring at top of file:
"""
📦 TOOL CATEGORIES (93 tools):
✅ Device Control (4 tools) - Lights, switches, climate, covers
✅ File Operations (9 tools) - Full /config access
✅ Automations (10 tools) - Create, update, trigger, manage
✅ Scenes (3 tools) - Activate, create, list
✅ Media & Devices (4 tools) - Vacuum, fan, camera, media
✅ System (2 tools) - Restart, call service
✅ Code Execution (3 tools) - Python sandbox, YAML, templates
✅ Discovery (5 tools) - States, areas, devices, entities
✅ Logs & History (6 tools) - Entity history, diagnostics, statistics
✅ Dashboards (9 tools) - Lovelace management
✅ Intelligence (4 tools) - Context, activity, comfort, energy
✅ Security (3 tools) - Monitoring, anomaly detection, presence
✅ Camera VLM (3 tools) - Vision AI analysis
✅ Add-on Management (9 tools) - Requires admin token
✅ Native MCPO Tools (12 tools) - Standard HA MCP tools with Pydantic
✅ System Diagnostics (4 tools) - Logs, notifications, integration status
"""
