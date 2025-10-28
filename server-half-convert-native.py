       # ... existing code ...

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    
    return [
        # =================================================================
        # CATEGORY 1: DEVICE DISCOVERY & STATE MANAGEMENT (NEW)
        # =================================================================
        
        Tool(
            name="discover_devices",
            description=(
                "Discover all available Home Assistant devices and entities organized by domain with current states and area assignments. "
                "WHEN TO USE: Use this FIRST when you need to know what devices exist before controlling them, especially when entity names are unknown. "
                "Essential for answering questions like 'What lights do I have?' or 'Show me all bedroom devices'. "
                "Returns organized lists with entity_ids, friendly names, current states, and area/room assignments. "
                "\n"
                "EXAMPLES:\n"
                "• 'What lights do I have in the bedroom?' → discover_devices(domain='light', area='bedroom')\n"
                "• 'Show me all my switches' → discover_devices(domain='switch')\n"
                "• 'List all devices' → discover_devices(domain='all')\n"
                "• 'What's in the living room?' → discover_devices(area='living_room')\n"
                "\n"
                "FILTERS: Combine domain + area for precise discovery (e.g., bedroom lights only). "
                "Use 'all' domain to see everything in a specific area."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": (
                            "Device domain to filter by. Examples: "
                            "'light' (all lights), 'switch' (switches/outlets), 'sensor' (temperature/humidity sensors), "
                            "'media_player' (TVs/speakers), 'climate' (thermostats), 'cover' (blinds/curtains), "
                            "'lock' (smart locks), 'camera' (security cameras). "
                            "Use 'all' to see all domains. Default: 'all'"
                        ),
                        "enum": [
                            "all", "light", "switch", "sensor", "binary_sensor", 
                            "media_player", "climate", "cover", "lock", "camera",
                            "alarm_control_panel", "vacuum", "fan", "scene", "automation"
                        ]
                    },
                    "area": {
                        "type": "string",
                        "description": (
                            "Area/room to filter by. Format: lowercase with underscores (e.g., 'living_room', 'master_bedroom'). "
                            "Examples: 'bedroom', 'kitchen', 'living_room', 'bathroom', 'office', 'garage'. "
                            "Omit to see devices from all areas."
                        )
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="get_device_state",
            description=(
                "Get the current state and all attributes of a specific device entity. "
                "Returns comprehensive information including state (on/off/open/closed), brightness, color, temperature, battery level, "
                "last changed time, and ALL device-specific attributes. "
                "WHEN TO USE: When you need detailed current state of a KNOWN entity_id. For unknown devices, use discover_devices() first. "
                "Perfect for answering 'Is the X on?', 'What's the current temperature?', 'What color is the light set to?'. "
                "\n"
                "EXAMPLES:\n"
                "• 'Is the living room light on?' → get_device_state(entity_id='light.living_room')\n"
                "• 'What's the bedroom temperature?' → get_device_state(entity_id='sensor.bedroom_temperature')\n"
                "• 'Check front door lock status' → get_device_state(entity_id='lock.front_door')\n"
                "• 'What brightness is the kitchen light?' → get_device_state(entity_id='light.kitchen')\n"
                "\n"
                "ENTITY_ID FORMAT: domain.area_name or domain.area_device\n"
                "Examples: light.living_room, sensor.temperature_bedroom, switch.coffee_maker, climate.thermostat\n"
                "\n"
                "RETURNED DATA: Includes state (e.g., 'on', 'off', '22.5°C'), friendly_name, last_changed, last_updated, "
                "and domain-specific attributes (brightness 0-255 for lights, temperature for climate, battery_level for sensors, etc.)"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": (
                            "The entity ID to query. Format: domain.identifier "
                            "Examples: 'light.living_room' (light in living room), 'sensor.bedroom_temperature' (temperature sensor), "
                            "'switch.coffee_maker' (smart outlet), 'lock.front_door' (smart lock), "
                            "'media_player.living_room_tv' (TV), 'climate.thermostat' (thermostat). "
                            "Must be exact entity_id - use discover_devices() if uncertain."
                        )
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="get_area_devices",
            description=(
                "Get all devices in a specific area/room grouped by device type with current states. "
                "Returns organized lists of lights, switches, sensors, media players, and other devices in the specified area. "
                "WHEN TO USE: When you know the room/area name and want to see or control ALL devices in that space. "
                "Perfect for whole-room operations like 'Turn off everything in the bedroom' or 'What's in the kitchen?'. "
                "More focused than discover_devices() when you know the target area."
                "\n"
                "EXAMPLES:\n"
                "• 'What devices are in the bedroom?' → get_area_devices(area='bedroom')\n"
                "• 'Show me all living room lights' → get_area_devices(area='living_room', device_types=['light'])\n"
                "• 'List kitchen lights and switches' → get_area_devices(area='kitchen', device_types=['light', 'switch'])\n"
                "• 'What's in the office?' → get_area_devices(area='office')\n"
                "\n"
                "AREA NAMING: Use lowercase with underscores. Examples: 'living_room', 'master_bedroom', 'guest_bathroom', 'home_office'\n"
                "\n"
                "DEVICE_TYPES FILTER: Optionally filter by types. Examples: ['light'], ['light', 'switch'], ['media_player', 'climate']. "
                "Omit to see ALL device types in the area."
                "\n"
                "RETURNED DATA: Devices grouped by type (lights: [...], switches: [...], sensors: [...]) with entity_ids, names, and current states."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": (
                            "Area/room name. Format: lowercase with underscores. "
                            "Examples: 'bedroom', 'living_room', 'kitchen', 'bathroom', 'office', 'garage', 'hallway', "
                            "'master_bedroom', 'guest_room', 'dining_room', 'laundry_room'. "
                            "Must match your Home Assistant area configuration exactly."
                        )
                    },
                    "device_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Optional filter for device types. Valid values: 'light', 'switch', 'sensor', 'binary_sensor', "
                            "'media_player', 'climate', 'cover', 'lock', 'camera', 'fan'. "
                            "Examples: ['light'] (only lights), ['light', 'switch'] (lights and switches), "
                            "['media_player', 'climate'] (media and climate devices). "
                            "Omit to return all device types in the area."
                        )
                    }
                },
                "required": ["area"]
            }
        ),
        
        # File System Tools (existing 9 tools)
        Tool(
            name="read_file",
            description="Read file content from Home Assistant config directory. Direct file system access - no SSH needed!",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Relative path from /config (e.g., 'packages/kitchen.yaml')"
                    }
                },
                "required": ["filepath"]
            }
        ),
        
        Tool(
            name="write_file",
            description="Write or update file in Home Assistant config directory. Creates backup automatically.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Relative path from /config"},
                    "content": {"type": "string", "description": "File content"},
                    "create_backup": {"type": "boolean", "description": "Create backup (default: true)", "default": True}
                },
                "required": ["filepath", "content"]
            }
        ),
        
        Tool(
            name="list_directory",
            description="List files and directories",
            inputSchema={
                "type": "object",
                "properties": {
                    "dirpath": {"type": "string", "description": "Directory path (default: '.')", "default": "."}
                }
            }
        ),
        
        Tool(
            name="get_directory_tree",
            description="Get recursive directory tree structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "dirpath": {"type": "string", "description": "Starting directory", "default": "."},
                    "max_depth": {"type": "integer", "description": "Maximum recursion depth", "default": 5}
                }
            }
        ),
        
        Tool(
            name="create_directory",
            description="Create new directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "dirpath": {"type": "string", "description": "Directory path to create"}
                },
                "required": ["dirpath"]
            }
        ),
        
        Tool(
            name="delete_file",
            description="Delete file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to delete"}
                },
                "required": ["filepath"]
            }
        ),
        
        Tool(
            name="move_file",
            description="Move or rename file/directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Source path"},
                    "destination": {"type": "string", "description": "Destination path"}
                },
                "required": ["source", "destination"]
            }
        ),
        
        Tool(
            name="copy_file",
            description="Copy file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Source path"},
                    "destination": {"type": "string", "description": "Destination path"}
                },
                "required": ["source", "destination"]
            }
        ),
        
        Tool(
            name="search_files",
            description="Search files by content pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Search pattern"},
                    "directory": {"type": "string", "description": "Directory to search", "default": "."},
                    "extensions": {"type": "array", "items": {"type": "string"}, "description": "File extensions to search"}
                },
                "required": ["pattern"]
            }
        ),
        
        # Home Assistant API Tools (existing 3 tools)
        Tool(
            name="get_states",
            description="Get Home Assistant entity states with optional filtering and pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Filter by domain (e.g., 'light', 'switch', 'sensor'). Optional."
                    },
                    "entity_id_pattern": {
                        "type": "string",
                        "description": "Filter by entity ID pattern (regex). Optional."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of entities to return (default: 50, max: 500)",
                        "default": 50
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of entities to skip for pagination (default: 0)",
                        "default": 0
                    }
                }
            }
        ),
        
        Tool(
            name="get_state",
            description="Get specific entity state",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Entity ID (e.g., 'light.kitchen')"}
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="call_service",
            description="Call Home Assistant service",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Service domain (e.g., 'light')"},
                    "service": {"type": "string", "description": "Service name (e.g., 'turn_on')"},
                    "entity_id": {"type": "string", "description": "Target entity ID"},
                    "data": {"type": "object", "description": "Service data"}
                },
                "required": ["domain", "service"]
            }
        ),
    ]
# ... rest of code ... 
        
        "@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    \"\"\"Handle tool calls\"\"\"
    
    try:
        # =================================================================
        # CATEGORY 1: DEVICE DISCOVERY & STATE MANAGEMENT (NEW)
        # =================================================================
        
        if name == "discover_devices":
            # Get all states from HA
            all_states = await ha_api.get_states()
            
            # Apply filters
            domain_filter = arguments.get("domain", "all").lower()
            area_filter = arguments.get("area", "").lower()
            
            # Group by domain
            devices_by_domain = {}
            
            for state in all_states:
                entity_id = state.get("entity_id", "")
                domain = entity_id.split(".")[0] if "." in entity_id else "unknown"
                
                # Apply domain filter
                if domain_filter != "all" and domain != domain_filter:
                    continue
                
                # Extract area information from attributes
                attributes = state.get("attributes", {})
                area_name = attributes.get("friendly_name", "").lower()
                
                # Apply area filter (check both friendly_name and other area-related attributes)
                if area_filter:
                    area_match = False
                    # Check friendly_name
                    if area_filter in area_name:
                        area_match = True
                    # Check other common area attributes
                    for attr_key in ["area", "room", "location"]:
                        if attr_key in attributes and area_filter in str(attributes[attr_key]).lower():
                            area_match = True
                            break
                    
                    if not area_match:
                        continue
                
                # Add to domain group
                if domain not in devices_by_domain:
                    devices_by_domain[domain] = []
                
                devices_by_domain[domain].append({
                    "entity_id": entity_id,
                    "friendly_name": attributes.get("friendly_name", entity_id),
                    "state": state.get("state"),
                    "area": attributes.get("area", "unknown"),
                    "last_changed": state.get("last_changed"),
                    "attributes": attributes
                })
            
            # Build response
            response = {
                "discovered_devices": devices_by_domain,
                "summary": {
                    "total_domains": len(devices_by_domain),
                    "total_devices": sum(len(devices) for devices in devices_by_domain.values()),
                    "filters_applied": {
                        "domain": domain_filter,
                        "area": area_filter if area_filter else "none"
                    }
                }
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
        elif name == "get_device_state":
            entity_id = arguments["entity_id"]
            
            # Get specific entity state
            state = await ha_api.get_state(entity_id)
            
            if not state or "error" in state:
                return [TextContent(type="text", text=json.dumps({
                    "error": f"Entity '{entity_id}' not found or unavailable",
                    "entity_id": entity_id
                }, indent=2))]
            
            # Build comprehensive device state response
            attributes = state.get("attributes", {})
            
            # Extract domain-specific information
            domain = entity_id.split(".")[0] if "." in entity_id else "unknown"
            domain_info = {}
            
            if domain == "light":
                domain_info = {
                    "brightness": attributes.get("brightness"),
                    "color_temp": attributes.get("color_temp"),
                    "rgb_color": attributes.get("rgb_color"),
                    "hs_color": attributes.get("hs_color"),
                    "supported_color_modes": attributes.get("supported_color_modes", [])
                }
            elif domain == "sensor":
                domain_info = {
                    "unit_of_measurement": attributes.get("unit_of_measurement"),
                    "device_class": attributes.get("device_class"),
                    "state_class": attributes.get("state_class")
                }
            elif domain == "climate":
                domain_info = {
                    "temperature": attributes.get("temperature"),
                    "target_temp": attributes.get("target_temp"),
                    "hvac_mode": attributes.get("hvac_mode"),
                    "hvac_modes": attributes.get("hvac_modes", []),
                    "min_temp": attributes.get("min_temp"),
                    "max_temp": attributes.get("max_temp")
                }
            elif domain == "media_player":
                domain_info = {
                    "media_title": attributes.get("media_title"),
                    "media_artist": attributes.get("media_artist"),
                    "media_album": attributes.get("media_album"),
                    "volume_level": attributes.get("volume_level"),
                    "is_muted": attributes.get("is_muted"),
                    "source": attributes.get("source"),
                    "supported_features": attributes.get("supported_features", [])
                }
            elif domain == "cover":
                domain_info = {
                    "current_position": attributes.get("current_position"),
                    "current_tilt_position": attributes.get("current_tilt_position"),
                    "is_opening": attributes.get("is_opening"),
                    "is_closing": attributes.get("is_closing"),
                    "supported_features": attributes.get("supported_features", [])
                }
            
            response = {
                "entity_id": entity_id,
                "domain": domain,
                "state": state.get("state"),
                "friendly_name": attributes.get("friendly_name", entity_id),
                "last_changed": state.get("last_changed"),
                "last_updated": state.get("last_updated"),
                "area_id": attributes.get("area_id"),
                "device_class": attributes.get("device_class"),
                "domain_specific": domain_info,
                "all_attributes": attributes
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
        elif name == "get_area_devices":
            area_name = arguments["area"].lower()
            device_types_filter = arguments.get("device_types", [])
            
            # Get all states from HA
            all_states = await ha_api.get_states()
            
            # Group devices by type in the specified area
            devices_by_type = {}
            
            for state in all_states:
                entity_id = state.get("entity_id", "")
                domain = entity_id.split(".")[0] if "." in entity_id else "unknown"
                
                # Apply device type filter
                if device_types_filter and domain not in device_types_filter:
                    continue
                
                # Check if device belongs to the specified area
                attributes = state.get("attributes", {})
                belongs_to_area = False
                
                # Check multiple area-related attributes
                area_indicators = [
                    attributes.get("area_id", ""),
                    attributes.get("area", ""),
                    attributes.get("room", ""),
                    attributes.get("location", ""),
                    attributes.get("friendly_name", "").lower()
                ]
                
                for indicator in area_indicators:
                    if area_name in str(indicator).lower():
                        belongs_to_area = True
                        break
                
                if not belongs_to_area:
                    continue
                
                # Add to device type group
                if domain not in devices_by_type:
                    devices_by_type[domain] = []
                
                devices_by_type[domain].append({
                    "entity_id": entity_id,
                    "friendly_name": attributes.get("friendly_name", entity_id),
                    "state": state.get("state"),
                    "last_changed": state.get("last_changed"),
                    "area_id": attributes.get("area_id"),
                    "attributes": attributes
                })
            
            # Build response
            response = {
                "area": arguments["area"],
                "devices_by_type": devices_by_type,
                "summary": {
                    "total_device_types": len(devices_by_type),
                    "total_devices": sum(len(devices) for devices in devices_by_type.values()),
                    "device_types_found": list(devices_by_type.keys()),
                    "filters_applied": {
                        "area": arguments["area"],
                        "device_types": device_types_filter if device_types_filter else "all"
                    }
                }
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
        # =================================================================
        # EXISTING FILE SYSTEM OPERATIONS
        # =================================================================
        
        elif name == "read_file":
            content = await file_mgr.read_file(arguments["filepath"])
            return [TextContent(type="text", text=content)]
        
        elif name == "write_file":
            result = await file_mgr.write_file(
                arguments["filepath"],
                arguments["content"],
                arguments.get("create_backup", True)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "list_directory":
            items = await file_mgr.list_directory(arguments.get("dirpath", "."))
            return [TextContent(type="text", text=json.dumps(items, indent=2))]
        
        elif name == "get_directory_tree":
            tree = await file_mgr.get_directory_tree(
                arguments.get("dirpath", "."),
                arguments.get("max_depth", 5)
            )
            return [TextContent(type="text", text=json.dumps(tree, indent=2))]
        
        elif name == "create_directory":
            result = await file_mgr.create_directory(arguments["dirpath"])
            return [TextContent(type="text", text=result)]
        
        elif name == "delete_file":
            result = await file_mgr.delete_file(arguments["filepath"])
            return [TextContent(type="text", text=result)]
        
        elif name == "move_file":
            result = await file_mgr.move_file(arguments["source"], arguments["destination"])
            return [TextContent(type="text", text=result)]
        
        elif name == "copy_file":
            result = await file_mgr.copy_file(arguments["source"], arguments["destination"])
            return [TextContent(type="text", text=result)]
        
        elif name == "search_files":
            matches = await file_mgr.search_files(
                arguments["pattern"],
                arguments.get("directory", "."),
                arguments.get("extensions")
            )
            return [TextContent(type="text", text=json.dumps(matches, indent=2))]
        
        # =================================================================
        # EXISTING HOME ASSISTANT API OPERATIONS
        # =================================================================
        
        elif name == "get_states":
            # Get all states from HA
            all_states = await ha_api.get_states()
            
            # Apply filtering
            filtered_states = all_states
            
            # Filter by domain if specified
            if "domain" in arguments and arguments["domain"]:
                domain = arguments["domain"].lower()
                filtered_states = [
                    state for state in filtered_states 
                    if state.get("entity_id", "").startswith(f"{domain}.")
                ]
            
            # Filter by entity_id pattern if specified
            if "entity_id_pattern" in arguments and arguments["entity_id_pattern"]:
                import re
                pattern = re.compile(arguments["entity_id_pattern"], re.IGNORECASE)
                filtered_states = [
                    state for state in filtered_states
                    if pattern.search(state.get("entity_id", ""))
                ]
            
            # Apply pagination
            offset = arguments.get("offset", 0)
            limit = min(arguments.get("limit", 50), 500)  # Max 500 entities
            
            total_count = len(filtered_states)
            paginated_states = filtered_states[offset:offset + limit]
            
            # Build response with metadata
            response = {
                "states": paginated_states,
                "metadata": {
                    "total": total_count,
                    "returned": len(paginated_states),
                    "offset": offset,
                    "limit": limit,
                    "has_more": (offset + limit) < total_count
                }
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
        elif name == "get_state":
            state = await ha_api.get_state(arguments["entity_id"])
            return [TextContent(type="text", text=json.dumps(state, indent=2))]
        
        elif name == "call_service":
            service_data = arguments.get("data", {})
            if "entity_id" in arguments:
                service_data["entity_id"] = arguments["entity_id"]
            
            result = await ha_api.call_service(
                arguments["domain"],
                arguments["service"],
                service_data
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Tool execution failed: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]
# ... rest of code ..."
        
        # =================================================================
        # CATEGORY 2: ADVANCED LIGHTING CONTROL (NEW)
        # =================================================================
        
        elif name == "adaptive_lighting":
            area = arguments["area"]
            activity = arguments["activity"]
            brightness_override = arguments.get("brightness_override")
            transition_seconds = arguments.get("transition_seconds", 2)
            
            # Define activity-based lighting presets
            activity_presets = {
                "work": {"brightness": 220, "color_temp": 4500, "description": "Bright, cool white for focus"},
                "relax": {"brightness": 120, "color_temp": 2700, "description": "Warm, dim for relaxation"},
                "reading": {"brightness": 200, "color_temp": 4000, "description": "Bright, neutral for reading"},
                "movie": {"brightness": 80, "color_temp": 3000, "description": "Dim, warm for movies"},
                "dinner": {"brightness": 150, "color_temp": 2800, "description": "Warm, moderate for dining"},
                "sleep": {"brightness": 40, "color_temp": 2200, "description": "Very dim, very warm for sleep"},
                "cooking": {"brightness": 255, "color_temp": 5000, "description": "Bright, cool white for cooking"},
                "exercise": {"brightness": 200, "color_temp": 4200, "description": "Bright, neutral for exercise"}
            }
            
            if activity not in activity_presets:
                return [TextContent(type="text", text=json.dumps({
                    "error": f"Unknown activity: {activity}. Valid: {list(activity_presets.keys())}"
                }, indent=2))]
            
            preset = activity_presets[activity]
            brightness = brightness_override if brightness_override is not None else preset["brightness"]
            color_temp = preset["color_temp"]
            
            # Get all lights in the area
            area_lights = await ha_api.call_api("GET", f"states?filter=area={area}&domain=light")
            
            if not area_lights or len(area_lights) == 0:
                return [TextContent(type="text", text=json.dumps({
                    "error": f"No lights found in area: {area}",
                    "area": area,
                    "suggestion": "Use discover_devices() to find available lights and areas"
                }, indent=2))]
            
            # Apply adaptive lighting to all lights in area
            results = []
            for light_state in area_lights:
                entity_id = light_state.get("entity_id")
                if not entity_id:
                    continue
                
                # Build service call data
                service_data = {
                    "entity_id": entity_id,
                    "brightness": brightness,
                    "color_temp": color_temp,
                    "transition": transition_seconds
                }
                
                # Call light.turn_on service
                result = await ha_api.call_service("light", "turn_on", service_data)
                results.append({
                    "entity_id": entity_id,
                    "activity": activity,
                    "brightness": brightness,
                    "color_temp": color_temp,
                    "transition": transition_seconds,
                    "preset_description": preset["description"],
                    "result": result
                })
            
            response = {
                "area": area,
                "activity": activity,
                "preset_applied": preset,
                "lights_controlled": len(results),
                "results": results,
                "summary": f"Applied {activity} lighting to {len(results)} lights in {area}: {preset['description']}"
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
        elif name == "circadian_lighting":
            area = arguments["area"]
            enable = arguments.get("enable", True)
            latitude = arguments.get("latitude")
            longitude = arguments.get("longitude")
            max_brightness = arguments.get("max_brightness", 255)
            
            if not enable:
                # Disable circadian mode - turn off all lights in area
                area_lights = await ha_api.call_api("GET", f"states?filter=area={area}&domain=light")
                results = []
                for light_state in area_lights:
                    entity_id = light_state.get("entity_id")
                    if entity_id:
                        result = await ha_api.call_service("light", "turn_off", {"entity_id": entity_id})
                        results.append({"entity_id": entity_id, "action": "turned_off", "result": result})
                
                return [TextContent(type="text", text=json.dumps({
                    "area": area,
                    "circadian_mode": "disabled",
                    "lights_controlled": len(results),
                    "results": results
                }, indent=2))]
            
            # Calculate sun position for circadian lighting
            from datetime import datetime, timezone
            import math
            
            # Use provided coordinates or get from HA config
            if latitude is None or longitude is None:
                # Get HA sun integration data
                sun_data = await ha_api.call_api("GET", "states/sun.sun")
                if sun_data:
                    # Extract coordinates from sun entity attributes
                    attributes = sun_data.get("attributes", {})
                    latitude = attributes.get("latitude")
                    longitude = attributes.get("longitude")
            
            if latitude is None or longitude is None:
                return [TextContent(type="text", text=json.dumps({
                    "error": "Could not determine location for circadian lighting. Provide latitude/longitude or ensure sun integration is configured."
                }, indent=2))]
            
            # Calculate sun elevation angle
            now = datetime.now(timezone.utc)
            # Simplified sun position calculation
            day_of_year = now.timetuple().tm_yday
            declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
            
            hour_angle = 15 * (now.hour - 12)  # 15 degrees per hour from solar noon
            latitude_rad = math.radians(latitude)
            elevation = math.degrees(math.asin(
                math.sin(latitude_rad) * math.sin(math.radians(declination)) +
                math.cos(latitude_rad) * math.cos(math.radians(declination)) * math.cos(math.radians(hour_angle))
            ))
            
            # Calculate circadian brightness and color temperature based on sun elevation
            if elevation > 0:
                # Daytime - brightness and color temperature based on sun elevation
                brightness_factor = min(1.0, elevation / 90.0)
                brightness = int(max_brightness * brightness_factor)
                
                # Color temperature: warm at sunrise/sunset, cool at noon
                if elevation < 10:
                    color_temp = 2700  # Very warm (sunrise/sunset)
                elif elevation < 30:
                    color_temp = 3500  # Warm (morning/evening)
                elif elevation < 60:
                    color_temp = 4500  # Neutral (mid-morning/afternoon)
                else:
                    color_temp = 5500  # Cool (midday)
            else:
                # Nighttime - very dim warm light
                brightness = int(max_brightness * 0.05)  # 5% of max
                color_temp = 2200  # Very warm
            
            # Apply circadian lighting to all lights in area
            area_lights = await ha_api.call_api("GET", f"states?filter=area={area}&domain=light")
            results = []
            
            for light_state in area_lights:
                entity_id = light_state.get("entity_id")
                if not entity_id:
                    continue
                
                service_data = {
                    "entity_id": entity_id,
                    "brightness": brightness,
                    "color_temp": color_temp,
                    "transition": 5  # Smooth transition for circadian changes
                }
                
                result = await ha_api.call_service("light", "turn_on", service_data)
                results.append({
                    "entity_id": entity_id,
                    "sun_elevation": elevation,
                    "brightness": brightness,
                    "color_temp": color_temp,
                    "result": result
                })
            
            response = {
                "area": area,
                "circadian_mode": "enabled",
                "sun_elevation": elevation,
                "calculated_brightness": brightness,
                "calculated_color_temp": color_temp,
                "lights_controlled": len(results),
                "results": results
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
        elif name == "multi_room_lighting_sync":
            areas = arguments["areas"]
            brightness = arguments.get("brightness")
            color_temp = arguments.get("color_temperature")
            transition_seconds = arguments.get("transition_seconds", 0)
            
            if len(areas) < 2:
                return [TextContent(type="text", text=json.dumps({
                    "error": "Multi-room lighting sync requires at least 2 areas. Use control_light() for single room."
                }, indent=2))]
            
            all_results = []
            total_lights_controlled = 0
            
            for area in areas:
                # Get all lights in this area
                area_lights = await ha_api.call_api("GET", f"states?filter=area={area}&domain=light")
                
                for light_state in area_lights:
                    entity_id = light_state.get("entity_id")
                    if not entity_id:
                        continue
                    
                    # Build service call data
                    service_data = {"entity_id": entity_id}
                    
                    if brightness is not None:
                        service_data["brightness"] = brightness
                    if color_temp is not None:
                        service_data["color_temp"] = color_temp
                    if transition_seconds > 0:
                        service_data["transition"] = transition_seconds
                    
                    # Call light service
                    result = await ha_api.call_service("light", "turn_on", service_data)
                    all_results.append({
                        "area": area,
                        "entity_id": entity_id,
                        "brightness": brightness,
                        "color_temp": color_temp,
                        "transition": transition_seconds,
                        "result": result
                    })
                    total_lights_controlled += 1
            
            response = {
                "areas_synced": areas,
                "total_lights_controlled": total_lights_controlled,
                "sync_settings": {
                    "brightness": brightness,
                    "color_temperature": color_temp,
                    "transition_seconds": transition_seconds
                },
                "results": all_results,
                "summary": f"Synchronized lighting across {len(areas)} areas, controlling {total_lights_controlled} lights"
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
        elif name == "presence_based_lighting":
            area = arguments["area"]
            motion_sensors = arguments.get("motion_sensors", [])
            lights_to_control = arguments.get("lights_to_control", [])
            timeout_minutes = arguments.get("timeout_minutes", 5)
            nightlight_mode = arguments.get("nightlight_mode", False)
            enable = arguments.get("enable", True)
            daylight_threshold = arguments.get("daylight_threshold", 100)
            
            if not enable:
                # Disable presence-based lighting - turn off all specified lights
                results = []
                for light_entity in lights_to_control:
                    result = await ha_api.call_service("light", "turn_off", {"entity_id": light_entity})
                    results.append({"entity_id": light_entity, "action": "turned_off", "result": result})
                
                return [TextContent(type="text", text=json.dumps({
                    "area": area,
                    "presence_mode": "disabled",
                    "lights_controlled": len(results),
                    "results": results
                }, indent=2))]
            
            # Get current motion sensor states
            motion_detected = False
            current_light_states = {}
            
            for sensor in motion_sensors:
                sensor_state = await ha_api.call_api("GET", f"states/{sensor}")
                if sensor_state and sensor_state.get("state") == "on":
                    motion_detected = True
                    break
            
            # Get current light states
            for light_entity in lights_to_control:
                light_state = await ha_api.call_api("GET", f"states/{light_entity}")
                if light_state:
                    current_light_states[light_entity] = {
                        "state": light_state.get("state"),
                        "last_changed": light_state.get("last_changed")
                    }
            
            # Get ambient light level if available
            ambient_light = 0
            for sensor in motion_sensors:
                sensor_state = await ha_api.call_api("GET", f"states/{sensor}")
                if sensor_state:
                    attributes = sensor_state.get("attributes", {})
                    if "illuminance" in attributes:
                        ambient_light = max(ambient_light, attributes.get("illuminance", 0))
                    elif "lux" in attributes:
                        ambient_light = max(ambient_light, attributes.get("lux", 0))
            
            results = []
            
            if motion_detected:
                # Motion detected - turn on lights
                for light_entity in lights_to_control:
                    current_state = current_light_states.get(light_entity, {})
                    if current_state.get("state") != "on":
                        # Check daylight harvesting
                        if ambient_light >= daylight_threshold:
                            # Bright enough - don't turn on
                            results.append({
                                "entity_id": light_entity,
                                "action": "daylight_harvesting",
                                "ambient_light": ambient_light,
                                "result": "No action taken (sufficient daylight)"
                            })
                        else:
                            # Turn on light
                            brightness = 80 if nightlight_mode else 200
                            service_data = {
                                "entity_id": light_entity,
                                "brightness": brightness,
                                "transition": 1
                            }
                            
                            result = await ha_api.call_service("light", "turn_on", service_data)
                            results.append({
                                "entity_id": light_entity,
                                "action": "turned_on",
                                "brightness": brightness,
                                "ambient_light": ambient_light,
                                "nightlight_mode": nightlight_mode,
                                "result": result
                            })
                    else:
                        results.append({
                            "entity_id": light_entity,
                            "action": "already_on",
                            "current_state": current_state.get("state"),
                            "result": "No action needed"
                        })
            else:
                # No motion - check timeout and turn off if needed
                from datetime import datetime, timedelta
                
                for light_entity in lights_to_control:
                    current_state = current_light_states.get(light_entity, {})
                    if current_state.get("state") == "on":
                        last_changed = current_state.get("last_changed")
                        if last_changed:
                            # Parse last_changed timestamp
                            if isinstance(last_changed, str):
                                try:
                                    last_changed_time = datetime.fromisoformat(last_changed.replace('Z', '+00:00'))
                                except:
                                    # Fallback to current time
                                    last_changed_time = datetime.now()
                            else:
                                last_changed_time = last_changed
                            
                            time_since_on = datetime.now() - last_changed_time
                            
                            if time_since_on.total_seconds() / 60 >= timeout_minutes:
                                # Turn off light
                                result = await ha_api.call_service("light", "turn_off", {"entity_id": light_entity})
                                results.append({
                                    "entity_id": light_entity,
                                    "action": "timeout_turn_off",
                                    "minutes_since_on": time_since_on.total_seconds() / 60,
                                    "timeout_minutes": timeout_minutes,
                                    "result": result
                                })
                            else:
                                results.append({
                                    "entity_id": light_entity,
                                    "action": "still_on_within_timeout",
                                    "minutes_since_on": time_since_on.total_seconds() / 60,
                                    "timeout_minutes": timeout_minutes,
                                    "result": "No action needed"
                                })
                    else:
                        results.append({
                            "entity_id": light_entity,
                            "action": "already_off",
                            "current_state": current_state.get("state"),
                            "result": "No action needed"
                        })
            
            response = {
                "area": area,
                "presence_mode": "enabled",
                "motion_detected": motion_detected,
                "ambient_light_level": ambient_light,
                "timeout_minutes": timeout_minutes,
                "nightlight_mode": nightlight_mode,
                "daylight_threshold": daylight_threshold,
                "results": results
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
# Add these tools to the @app.list_tools() function, after the device discovery tools

        # =================================================================
        # CATEGORY 2: ADVANCED LIGHTING CONTROL (NEW)
        # =================================================================
        
        Tool(
            name="adaptive_lighting",
            description=(
                "🧠 INTELLIGENT: Adjust lighting based on current activity, time of day, and ambient conditions. "
                "Uses sun position, time-based preferences, and activity detection to create optimal lighting environments. "
                "WHEN TO USE: When you want smart, automatic lighting that adapts to your needs and preferences. "
                "Perfect for 'I'm working', 'I'm relaxing', 'It's evening', etc. "
                "\n"
                "EXAMPLES:\n"
                "• 'I'm working in the office' → adaptive_lighting(area='office', activity='work')\n"
                "• 'Set evening mood lighting' → adaptive_lighting(area='living_room', activity='relax')\n"
                "• 'I'm reading in bed' → adaptive_lighting(area='bedroom', activity='reading')\n"
                "• 'Movie time in living room' → adaptive_lighting(area='living_room', activity='movie')\n"
                "\n"
                "ACTIVITY MODES: 'work' (bright, cool white), 'relax' (warm, dim), 'reading' (bright, neutral), "
                "'movie' (dim, warm), 'dinner' (warm, moderate), 'sleep' (very dim, warm)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Area/room name (e.g., 'living_room', 'office', 'bedroom')"
                    },
                    "activity": {
                        "type": "string",
                        "enum": ["work", "relax", "reading", "movie", "dinner", "sleep", "cooking", "exercise"],
                        "description": "Activity type for optimal lighting settings"
                    },
                    "brightness_override": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 255,
                        "description": "Override brightness (0-255). Optional - uses activity defaults."
                    },
                    "transition_seconds": {
                        "type": "number",
                        "minimum": 0,
                        "description": "Transition duration in seconds. Default: 2 seconds."
                    }
                },
                "required": ["area", "activity"]
            }
        ),
        
        Tool(
            name="circadian_lighting",
            description=(
                "🌅 CIRCADIAN: Automatically adjust lighting to match natural daylight patterns throughout the day. "
                "Uses sun position, time of day, and seasonal changes to maintain healthy circadian rhythm. "
                "WHEN TO USE: For automatic, health-conscious lighting that follows natural patterns. "
                "Perfect for all-day use in main living areas."
                "\n"
                "EXAMPLES:\n"
                "• 'Set up circadian lighting in living room' → circadian_lighting(area='living_room')\n"
                "• 'Enable natural light patterns' → circadian_lighting(area='office', enable=true)\n"
                "• 'Turn off circadian mode' → circadian_lighting(area='bedroom', enable=false)\n"
                "\n"
                "CIRCADIAN PATTERN: Morning (cool, bright), Midday (neutral, very bright), "
                "Evening (warm, moderate), Night (very warm, dim). Supports seasonal variations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Area/room name for circadian lighting"
                    },
                    "enable": {
                        "type": "boolean",
                        "description": "Enable or disable circadian mode. Default: true",
                        "default": true
                    },
                    "latitude": {
                        "type": "number",
                        "minimum": -90,
                        "maximum": 90,
                        "description": "Latitude for sun calculations. Optional - uses Home Assistant location."
                    },
                    "longitude": {
                        "type": "number",
                        "minimum": -180,
                        "maximum": 180,
                        "description": "Longitude for sun calculations. Optional - uses Home Assistant location."
                    },
                    "max_brightness": {
                        "type": "integer",
                        "minimum": 100,
                        "maximum": 255,
                        "description": "Maximum brightness during peak daytime. Default: 255."
                    }
                },
                "required": ["area"]
            }
        ),
        
        Tool(
            name="multi_room_lighting_sync",
            description=(
                "🏠 COORDINATION: Synchronize lighting settings across multiple rooms/areas simultaneously. "
                "Creates a cohesive, unified lighting experience where all specified rooms share the same brightness and color temperature. "
                "Perfect for open floor plans, entertaining guests, whole-home scenes, or creating flow between connected spaces. "
                "WHEN TO USE: When you want multiple rooms to have matching lighting (not individual room control). "
                "Great for 'all downstairs lights', 'entire first floor', 'open plan living'."
                "\n"
                "EXAMPLES:\n"
                "• 'Set all downstairs to 60% warm white' → multi_room_lighting_sync(areas=['living_room', 'kitchen', 'dining_room'], brightness=153, color_temperature=2700)\n"
                "• 'Brighten whole house to 80%' → multi_room_lighting_sync(areas=['living_room', 'bedroom', 'kitchen', 'bathroom'], brightness=204)\n"
                "• 'Dim all rooms to 30% for movie night' → multi_room_lighting_sync(areas=['living_room', 'dining_room', 'hallway'], brightness=77, transition_seconds=5)\n"
                "• 'Sync open plan to neutral white' → multi_room_lighting_sync(areas=['kitchen', 'dining_room', 'living_room'], color_temperature=4000)\n"
                "• 'Evening ambiance across home' → multi_room_lighting_sync(areas=['bedroom', 'living_room', 'kitchen'], brightness=102, color_temperature=2500, transition_seconds=10)\n"
                "\n"
                "BRIGHTNESS SYNC: All rooms set to same brightness (0-255 scale). "
                "Quick reference: 25%=64, 50%=128, 60%=153, 75%=191, 80%=204. "
                "COLOR TEMPERATURE SYNC: All rooms set to same Kelvin value (2000-6500K). "
                "2000-2700K=warm cozy, 3000-4000K=neutral, 4500-6500K=cool energizing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "List of area/room names to synchronize. All lights in these areas will be set to same settings. "
                            "Format: lowercase with underscores. "
                            "Examples: ['living_room', 'kitchen', 'dining_room'] (open plan), "
                            "['bedroom', 'bathroom'] (master suite), "
                            "['living_room', 'hallway', 'bedroom', 'bathroom'] (whole home). "
                            "Minimum 2 rooms - use control_light() for single room."
                        )
                    },
                    "brightness": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 255,
                        "description": (
                            "Synchronized brightness level (0-255 scale) applied to all rooms. "
                            "0=off, 255=max brightness. "
                            "Percentage conversions: 25%=64, 50%=128, 60%=153, 75%=191, 80%=204, 100%=255. "
                            "Optional - omit to keep current brightness and only sync color temperature."
                        )
                    },
                    "color_temperature": {
                        "type": "integer",
                        "minimum": 2000,
                        "maximum": 6500,
                        "description": (
                            "Synchronized color temperature in Kelvin (2000-6500K) applied to all rooms. "
                            "2000-2700K=warm white (cozy evening), 3000-4000K=neutral white (balanced), "
                            "4500-6500K=cool white/daylight (energizing morning). "
                            "Optional - omit to keep current color temperature and only sync brightness. "
                            "Only affects lights with tunable white capability."
                        )
                    },
                    "transition_seconds": {
                        "type": "number",
                        "minimum": 0,
                        "description": (
                            "Transition duration in seconds for smooth synchronized change. "
                            "0=instant (can be jarring), 3-5=smooth and user-friendly (recommended), "
                            "10+=very gradual (ambient mood shift). "
                            "Default: 0 (instant). Recommend 3-5 seconds for pleasant synchronized transitions."
                        )
                    }
                },
                "required": ["areas"]
            }
        ),
        
        Tool(
            name="presence_based_lighting",
            description=(
                "👤 INTELLIGENT: Adjust lighting based on presence detection and movement patterns. "
                "Uses motion sensors, room presence, and time-of-day to automatically control "
                "lights. Includes timeout settings and manual override detection. "
                "WHEN TO USE: For automatic lighting that responds to occupancy and saves energy. "
                "Perfect for hallways, bathrooms, closets, and rarely used rooms."
                "\n"
                "EXAMPLES:\n"
                "• 'Set up presence lighting in hallway' → presence_based_lighting(area='hallway', motion_sensors=['binary_sensor.hallway_motion'])\n"
                "• 'Enable bathroom motion lighting' → presence_based_lighting(area='bathroom', motion_sensors=['binary_sensor.bathroom_motion'], timeout_minutes=5)\n"
                "• 'Nightlight mode for hallway' → presence_based_lighting(area='hallway', motion_sensors=['binary_sensor.hallway_motion'], nightlight_mode=true, timeout_minutes=2)\n"
                "• 'Disable presence lighting' → presence_based_lighting(area='hallway', enable=false)\n"
                "\n"
                "FEATURES: Auto-on when motion detected, auto-off after timeout, "
                "nightlight mode (dim lighting after sunset), manual override detection, "
                "daylight harvesting (won't turn on if bright enough)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Area/room name for presence-based lighting"
                    },
                    "motion_sensors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Motion sensor entity IDs (e.g., ['binary_sensor.hallway_motion'])"
                    },
                    "lights_to_control": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Light entity IDs to control (optional - auto-discovers lights in area)"
                    },
                    "timeout_minutes": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 60,
                        "description": "Minutes of no motion before turning off (default: 5)"
                    },
                    "nightlight_mode": {
                        "type": "boolean",
                        "description": "Enable dimmed nightlight mode after sunset (default: false)"
                    },
                    "enable": {
                        "type": "boolean",
                        "description": "Enable or disable presence-based lighting (default: true)"
                    },
                    "daylight_threshold": {
                        "type": "integer",
                        "minimum": 10,
                        "maximum": 1000,
                        "description": "Lux threshold for daylight harvesting (default: 100 - won't turn on if brighter)"
                    }
                },
                "required": ["area"]
            }
        ),

# ... existing tools continue ...
# ... rest of existing code continues ...
        # =================================================================
        # CATEGORY 3: MEDIA PLAYER CONTROL (NEW)
        # =================================================================
        
        elif name == "control_media_player":
            entity_id = arguments["entity_id"]
            action = arguments["action"]
            volume_level = arguments.get("volume_level")
            source = arguments.get("source")
            
            # Build service call data
            service_data = {"entity_id": entity_id}
            
            if volume_level is not None:
                service_data["volume_level"] = volume_level
            if source is not None:
                service_data["source"] = source
            
            # Map action to HA service
            service_mapping = {
                "turn_on": "turn_on",
                "turn_off": "turn_off", 
                "play": "media_play",
                "pause": "media_pause",
                "stop": "media_stop",
                "next": "media_next_track",
                "previous": "media_previous_track",
                "volume_up": "volume_up",
                "volume_down": "volume_down",
                "volume_set": "volume_set",
                "mute": "volume_mute",
                "unmute": "volume_unmute",
                "toggle": "toggle",
                "select_source": "select_source"
            }
            
            if action not in service_mapping:
                return [TextContent(type="text", text=json.dumps({
                    "error": f"Unknown action: {action}. Valid: {list(service_mapping.keys())}",
                    "entity_id": entity_id
                }, indent=2))]
            
            # Call the appropriate service
            service_name = service_mapping[action]
            result = await ha_api.call_service("media_player", service_name, service_data)
            
            response = {
                "entity_id": entity_id,
                "action": action,
                "service_called": f"media_player.{service_name}",
                "service_data": service_data,
                "result": result
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
        elif name == "play_media":
            entity_id = arguments["entity_id"]
            media_content_id = arguments["media_content_id"]
            media_content_type = arguments.get("media_content_type", "music")
            extra = arguments.get("extra", {})
            
            # Build service call data
            service_data = {
                "entity_id": entity_id,
                "media_content_id": media_content_id,
                "media_content_type": media_content_type
            }
            
            # Add extra parameters
            service_data.update(extra)
            
            # Call media_play_media service
            result = await ha_api.call_service("media_player", "play_media", service_data)
            
            response = {
                "entity_id": entity_id,
                "media_content_id": media_content_id,
                "media_content_type": media_content_type,
                "extra_parameters": extra,
                "result": result
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
        elif name == "multi_room_audio_sync":
            areas = arguments["areas"]
            volume_level = arguments.get("volume_level", 0.5)
            sync_type = arguments.get("sync_type", "sync")
            source_content = arguments.get("source_content")
            fade_seconds = arguments.get("fade_seconds", 2)
            
            if len(areas) < 2:
                return [TextContent(type="text", text=json.dumps({
                    "error": "Multi-room audio sync requires at least 2 areas. Use control_media_player() for single room."
                }, indent=2))]
            
            all_results = []
            total_speakers_controlled = 0
            
            for area in areas:
                # Get all media players in this area
                area_media_players = await ha_api.call_api("GET", f"states?filter=area={area}&domain=media_player")
                
                for media_state in area_media_players:
                    entity_id = media_state.get("entity_id")
                    if not entity_id:
                        continue
                    
                    # Adjust volume based on sync type
                    adjusted_volume = volume_level
                    if sync_type == "party":
                        adjusted_volume = min(1.0, volume_level * 1.2)  # 20% louder for parties
                    elif sync_type == "ambient":
                        adjusted_volume = volume_level * 0.6  # 40% quieter for background
                    
                    # Build service call data
                    service_data = {"entity_id": entity_id}
                    
                    if adjusted_volume != 0.5:  # Only set if not default
                        service_data["volume_level"] = adjusted_volume
                    
                    if source_content:
                        service_data["media_content_id"] = source_content
                        service_data["media_content_type"] = "music"  # Assume music for sync
                    
                    if fade_seconds > 0:
                        service_data["fade"] = fade_seconds
                    
                    # Start playback or adjust volume
                    if source_content:
                        # Play new content
                        result = await ha_api.call_service("media_player", "play_media", service_data)
                        action = "play_content"
                    else:
                        # Just adjust volume of current playback
                        result = await ha_api.call_service("media_player", "volume_set", service_data)
                        action = "volume_adjust"
                    
                    all_results.append({
                        "area": area,
                        "entity_id": entity_id,
                        "sync_type": sync_type,
                        "volume_level": adjusted_volume,
                        "source_content": source_content,
                        "fade_seconds": fade_seconds,
                        "action": action,
                        "result": result
                    })
                    total_speakers_controlled += 1
            
            response = {
                "areas_synced": areas,
                "sync_type": sync_type,
                "base_volume_level": volume_level,
                "total_speakers_controlled": total_speakers_controlled,
                "source_content": source_content,
                "fade_seconds": fade_seconds,
                "results": all_results,
                "summary": f"Synchronized {sync_type} audio across {len(areas)} areas, controlling {total_speakers_controlled} speakers"
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
        elif name == "follow_me_audio":
            tracking_sensors = arguments["tracking_sensors"]
            speaker_areas = arguments["speaker_areas"]
            transition_delay = arguments.get("transition_delay", 30)
            volume_override = arguments.get("volume_override")
            enable = arguments.get("enable", True)
            
            if not enable:
                # Disable follow-me audio - stop all specified speakers
                results = []
                for area in speaker_areas:
                    area_speakers = await ha_api.call_api("GET", f"states?filter=area={area}&domain=media_player")
                    for media_state in area_speakers:
                        entity_id = media_state.get("entity_id")
                        if entity_id:
                            result = await ha_api.call_service("media_player", "media_stop", {"entity_id": entity_id})
                            results.append({"area": area, "entity_id": entity_id, "action": "stopped", "result": result})
                
                return [TextContent(type="text", text=json.dumps({
                    "follow_me_mode": "disabled",
                    "speaker_areas": speaker_areas,
                    "speakers_stopped": len(results),
                    "results": results
                }, indent=2))]
            
            # Get current motion sensor states to determine user location
            current_location = None
            motion_detected_areas = []
            
            for sensor in tracking_sensors:
                sensor_state = await ha_api.call_api("GET", f"states/{sensor}")
                if sensor_state and sensor_state.get("state") == "on":
                    # Extract area from sensor name or attributes
                    attributes = sensor_state.get("attributes", {})
                    sensor_area = attributes.get("area") or sensor.split(".")[-1] if "." in sensor else sensor
                    motion_detected_areas.append(sensor_area)
                    
                    # Use the first detected motion as current location
                    if current_location is None:
                        current_location = sensor_area
            
            if current_location is None:
                return [TextContent(type="text", text=json.dumps({
                    "error": "No motion detected in any tracking sensors. Cannot determine user location.",
                    "tracking_sensors": tracking_sensors,
                    "suggestion": "Check sensor names and ensure motion is being detected."
                }, indent=2))]
            
            # Determine which speaker areas to activate
            areas_to_activate = []
            
            # Prioritize current location area
            if current_location in speaker_areas:
                areas_to_activate.append(current_location)
            
            # Add adjacent areas based on typical home layout
            adjacent_areas = {
                "living_room": ["kitchen", "dining_room", "hallway"],
                "kitchen": ["living_room", "dining_room"],
                "bedroom": ["bathroom", "hallway"],
                "office": ["living_room", "kitchen"]
            }
            
            for area in speaker_areas:
                if area not in areas_to_activate and area in adjacent_areas.get(current_location, []):
                    areas_to_activate.append(area)
            
            results = []
            total_speakers_controlled = 0
            
            for area in areas_to_activate:
                area_speakers = await ha_api.call_api("GET", f"states?filter=area={area}&domain=media_player")
                
                for media_state in area_speakers:
                    entity_id = media_state.get("entity_id")
                    if not entity_id:
                        continue
                    
                    # Calculate appropriate volume
                    target_volume = volume_override or 0.4  # Default moderate volume
                    
                    # Adjust volume based on area priority
                    if area == current_location:
                        target_volume = volume_override or 0.6  # Higher volume in current room
                    elif area in adjacent_areas.get(current_location, []):
                        target_volume = volume_override or 0.3  # Medium volume in adjacent rooms
                    else:
                        target_volume = volume_override or 0.2  # Lower volume in distant rooms
                    
                    # Build service call data
                    service_data = {
                        "entity_id": entity_id,
                        "volume_level": target_volume,
                        "fade": transition_delay
                    }
                    
                    # Start or adjust playback
                    current_state = media_state.get("state")
                    if current_state != "playing":
                        # Start playback with volume
                        result = await ha_api.call_service("media_player", "media_play", service_data)
                        action = "started_with_volume"
                    else:
                        # Just adjust volume
                        result = await ha_api.call_service("media_player", "volume_set", service_data)
                        action = "volume_adjusted"
                    
                    results.append({
                        "area": area,
                        "entity_id": entity_id,
                        "current_location": current_location,
                        "area_priority": "current" if area == current_location else "adjacent" if area in adjacent_areas.get(current_location, []) else "distant",
                        "target_volume": target_volume,
                        "transition_delay": transition_delay,
                        "action": action,
                        "result": result
                    })
                    total_speakers_controlled += 1
            
            response = {
                "follow_me_mode": "enabled",
                "current_location": current_location,
                "motion_detected_areas": motion_detected_areas,
                "areas_to_activate": areas_to_activate,
                "total_speakers_controlled": total_speakers_controlled,
                "transition_delay": transition_delay,
                "volume_override": volume_override,
                "results": results
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

# ... rest of existing code continues...
