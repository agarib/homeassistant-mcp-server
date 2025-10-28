#!/usr/bin/env python3
"""
🏠 Home Assistant MCP Server - Native Add-on (Part 3: Dashboard & HACS Management)
CONVERTED TOOLS from external REST/SSH server to native HA addon

This file contains:
- Dashboard Discovery & Listing
- HACS Custom Card Creation (button-card, mushroom-card)
- Standard Dashboard Card Creation
- Card Editing & Deletion
- Dashboard Configuration Inspection

Total: ~9 dashboard management tools
"""

import json
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent


# ============================================================================
# PART 3: DASHBOARD TOOL DEFINITIONS (to add to list_tools() in server.py)
# ============================================================================

def get_part3_dashboard_tools() -> list[Tool]:
    """
    Returns Part 3 dashboard management tool definitions
    Copy these into the main list_tools() function
    """
    return [
        # =================================================================
        # DASHBOARD DISCOVERY & LISTING
        # =================================================================
        
        Tool(
            name="list_dashboards",
            description=(
                "📱 **List All Home Assistant Dashboards**\n\n"
                "Shows dashboard names, URLs, and configuration modes (storage/yaml). "
                "WHEN TO USE: To see available dashboards before adding/editing cards. "
                "First step in dashboard management."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        Tool(
            name="discover_dashboards",
            description=(
                "🔍 **Enhanced Dashboard Discovery**\n\n"
                "List all dashboards with IDs, titles, and metadata. Filter by type. "
                "WHEN TO USE: To explore available dashboards with detailed information.\n\n"
                "**EXAMPLES:**\n"
                "• 'Show all dashboards' → discover_dashboards()\n"
                "• 'List mobile views' → discover_dashboards(dashboard_type='mobile')\n"
                "• 'Show panel views' → discover_dashboards(dashboard_type='panel')"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard_type": {
                        "type": "string",
                        "enum": ["all", "mobile", "desktop", "panel", "storage", "yaml"],
                        "description": "Filter by type: all, mobile, desktop, panel, storage, yaml"
                    },
                    "include_cards": {
                        "type": "boolean",
                        "description": "Include card count for each dashboard",
                        "default": False
                    }
                },
                "required": []
            }
        ),
        
        # =================================================================
        # HACS CUSTOM CARDS
        # =================================================================
        
        Tool(
            name="list_hacs_cards",
            description=(
                "📦 **List Installed HACS Custom Cards**\n\n"
                "Shows what custom cards are available for dashboard creation. "
                "WHEN TO USE: Before creating custom cards, to verify installation.\n\n"
                "**COMMON HACS CARDS:**\n"
                "• button-card - Highly customizable buttons\n"
                "• mushroom - Modern minimalist cards\n"
                "• mini-graph-card - Compact graphs\n"
                "• stack-in-card - Card stacking/grouping"
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        Tool(
            name="create_button_card",
            description=(
                "🎨 **HACS Button-Card Creation**\n\n"
                "Create customizable button-card (most popular HACS card). "
                "Highly flexible with custom colors, icons, tap actions.\n\n"
                "**EXAMPLES:**\n"
                "• Simple: 'Add button for bedroom light' → create_button_card(dashboard='mobile', entity_id='light.bedroom')\n"
                "• Advanced: 'Yellow moon button' → create_button_card(entity_id='light.bedroom', color='yellow', icon='mdi:weather-night')\n\n"
                "**FEATURES:** Custom colors, MDI icons, tap actions, show/hide state\n"
                "**REQUIRES:** button-card from HACS"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard": {
                        "type": "string",
                        "description": "Dashboard name (default, mobile, etc.)",
                        "default": "lovelace"
                    },
                    "entity_id": {
                        "type": "string",
                        "description": "Entity to control (light.*, switch.*, scene.*, script.*)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Button display name (optional)"
                    },
                    "icon": {
                        "type": "string",
                        "description": "MDI icon (mdi:lightbulb, mdi:power, etc.)"
                    },
                    "color": {
                        "type": "string",
                        "description": "CSS color (yellow, #FFD700, etc.)",
                        "default": "auto"
                    },
                    "tap_action": {
                        "type": "string",
                        "enum": ["toggle", "more-info", "call-service", "navigate", "none"],
                        "description": "Action when tapped",
                        "default": "toggle"
                    },
                    "show_state": {
                        "type": "boolean",
                        "description": "Show entity state",
                        "default": True
                    },
                    "show_name": {
                        "type": "boolean",
                        "description": "Show entity name",
                        "default": True
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="create_mushroom_card",
            description=(
                "🍄 **HACS Mushroom Card Creation**\n\n"
                "Create modern, minimalist mushroom-card. iOS-inspired design with rounded corners.\n\n"
                "**EXAMPLES:**\n"
                "• Simple: 'Add mushroom light card' → create_mushroom_card(card_type='light', entity_id='light.bedroom')\n"
                "• Advanced: 'Mushroom climate card' → create_mushroom_card(card_type='climate', entity_id='climate.living_room', fill_container=true)\n\n"
                "**CARD TYPES:** light, switch, climate, cover, person, entity\n"
                "**REQUIRES:** mushroom from HACS"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard": {
                        "type": "string",
                        "description": "Dashboard name",
                        "default": "lovelace"
                    },
                    "card_type": {
                        "type": "string",
                        "enum": ["light", "switch", "climate", "cover", "person", "entity"],
                        "description": "Mushroom card type"
                    },
                    "entity_id": {
                        "type": "string",
                        "description": "Entity to display/control"
                    },
                    "name": {
                        "type": "string",
                        "description": "Custom name override"
                    },
                    "icon": {
                        "type": "string",
                        "description": "Custom MDI icon"
                    },
                    "fill_container": {
                        "type": "boolean",
                        "description": "Fill container width",
                        "default": False
                    },
                    "show_temperature_control": {
                        "type": "boolean",
                        "description": "For climate: show temp slider",
                        "default": True
                    },
                    "layout": {
                        "type": "string",
                        "enum": ["horizontal", "vertical"],
                        "description": "Card layout",
                        "default": "horizontal"
                    }
                },
                "required": ["card_type", "entity_id"]
            }
        ),
        
        # =================================================================
        # STANDARD DASHBOARD CARDS
        # =================================================================
        
        Tool(
            name="create_dashboard_card",
            description=(
                "📋 **Standard Dashboard Card Creation**\n\n"
                "Create built-in Home Assistant card types (entities, glance, button, gauge, etc.).\n\n"
                "**EXAMPLES:**\n"
                "• Entities: 'Add bedroom lights card' → create_dashboard_card(card_type='entities', entities=['light.bedroom', 'light.bedside'])\n"
                "• Gauge: 'Add temp gauge' → create_dashboard_card(card_type='gauge', entity='sensor.temp', min=15, max=30)\n\n"
                "**CARD TYPES:** entities, glance, button, gauge, light, thermostat, picture-entity, history-graph"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard": {
                        "type": "string",
                        "description": "Dashboard name",
                        "default": "lovelace"
                    },
                    "card_type": {
                        "type": "string",
                        "enum": ["entities", "glance", "button", "gauge", "light", "thermostat", "picture-entity", "history-graph", "sensor", "weather-forecast"],
                        "description": "Standard Lovelace card type"
                    },
                    "entity": {
                        "type": "string",
                        "description": "Single entity for single-entity cards"
                    },
                    "entities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of entities for multi-entity cards"
                    },
                    "title": {
                        "type": "string",
                        "description": "Card title"
                    },
                    "name": {
                        "type": "string",
                        "description": "Entity display name override"
                    },
                    "icon": {
                        "type": "string",
                        "description": "Custom MDI icon"
                    },
                    "min": {
                        "type": "number",
                        "description": "Gauge minimum value"
                    },
                    "max": {
                        "type": "number",
                        "description": "Gauge maximum value"
                    }
                },
                "required": ["card_type"]
            }
        ),
        
        # =================================================================
        # CARD EDITING & DELETION
        # =================================================================
        
        Tool(
            name="edit_dashboard_card",
            description=(
                "✏️ **Edit Existing Dashboard Card**\n\n"
                "Modify card properties (colors, icons, name, tap actions). "
                "Works with standard and custom HACS cards.\n\n"
                "**EXAMPLES:**\n"
                "• 'Change bedroom button to yellow' → edit_dashboard_card(card_index=0, color='yellow')\n"
                "• 'Update icon to moon' → edit_dashboard_card(card_index=2, icon='mdi:weather-night')\n\n"
                "**CARD INDEX:** Cards numbered from 0. Use get_dashboard_config() to find indices."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard": {
                        "type": "string",
                        "description": "Dashboard name",
                        "default": "lovelace"
                    },
                    "card_index": {
                        "type": "integer",
                        "description": "Card position (0-based)"
                    },
                    "color": {
                        "type": "string",
                        "description": "New card color"
                    },
                    "icon": {
                        "type": "string",
                        "description": "New MDI icon"
                    },
                    "name": {
                        "type": "string",
                        "description": "New display name"
                    },
                    "entity_id": {
                        "type": "string",
                        "description": "New entity to control"
                    },
                    "tap_action": {
                        "type": "string",
                        "enum": ["toggle", "more-info", "call-service", "navigate", "none"],
                        "description": "New tap action"
                    },
                    "show_state": {
                        "type": "boolean",
                        "description": "Show/hide state"
                    },
                    "show_name": {
                        "type": "boolean",
                        "description": "Show/hide name"
                    }
                },
                "required": ["card_index"]
            }
        ),
        
        Tool(
            name="delete_dashboard_card",
            description=(
                "🗑️ **Delete Dashboard Card**\n\n"
                "Remove card from dashboard by index. Permanent deletion.\n\n"
                "**EXAMPLES:**\n"
                "• 'Remove first card' → delete_dashboard_card(card_index=0)\n"
                "• 'Delete bedroom button' → delete_dashboard_card(card_index=5)\n\n"
                "⚠️ **WARNING:** Deletion is permanent. Use get_dashboard_config() first to verify."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard": {
                        "type": "string",
                        "description": "Dashboard name",
                        "default": "lovelace"
                    },
                    "card_index": {
                        "type": "integer",
                        "description": "Card position to delete (0-based)"
                    }
                },
                "required": ["card_index"]
            }
        ),
        
        # =================================================================
        # DASHBOARD INSPECTION
        # =================================================================
        
        Tool(
            name="get_dashboard_config",
            description=(
                "🔍 **Inspect Dashboard Configuration**\n\n"
                "Retrieve complete dashboard config: all cards, views, settings. "
                "Shows card index positions for editing/deletion.\n\n"
                "**EXAMPLES:**\n"
                "• 'Show mobile dashboard cards' → get_dashboard_config(dashboard='mobile')\n"
                "• 'What's card 3?' → get_dashboard_config() then find index 3\n\n"
                "**RETURNS:** Dashboard title, mode, all cards with indices, card properties"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard": {
                        "type": "string",
                        "description": "Dashboard name to inspect",
                        "default": "lovelace"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="get_dashboard_card",
            description=(
                "🔎 **Get Single Card Details**\n\n"
                "Retrieve detailed configuration of specific card by index or ID.\n\n"
                "**EXAMPLES:**\n"
                "• 'Show kitchen energy card' → get_dashboard_card(dashboard_id='kitchen', card_index=2)\n"
                "• 'Check weather card' → get_dashboard_card(card_index=0)\n"
                "• 'List all cards' → get_dashboard_card(list_all=true)"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard_id": {
                        "type": "string",
                        "description": "Dashboard identifier",
                        "default": "lovelace"
                    },
                    "card_index": {
                        "type": "integer",
                        "description": "Card position (0-based)"
                    },
                    "card_id": {
                        "type": "string",
                        "description": "Card identifier (alternative to index)"
                    },
                    "list_all": {
                        "type": "boolean",
                        "description": "List all cards with indices",
                        "default": False
                    }
                },
                "required": []
            }
        ),
    ]


# ============================================================================
# PART 3: DASHBOARD TOOL HANDLERS (to add to call_tool() in server.py)
# ============================================================================

async def handle_part3_dashboard_tools(name: str, arguments: dict, ha_api, file_mgr) -> list[TextContent]:
    """
    Handler functions for Part 3 dashboard management tools
    Copy these elif blocks into the main call_tool() function
    
    NOTE: Dashboard operations use Lovelace API endpoints:
    - GET /api/lovelace/config - Get dashboard configuration
    - POST /api/lovelace/config - Update dashboard configuration
    - GET /api/lovelace/resources - List custom cards
    """
    
    # =================================================================
    # DASHBOARD DISCOVERY
    # =================================================================
    
    if name == "list_dashboards":
        try:
            # Get dashboard list via API
            dashboards_data = await ha_api.call_api("GET", "lovelace", None)
            
            result_text = "📱 **Available Dashboards:**\n\n"
            
            # Default dashboard always exists
            result_text += "• **Home** (`lovelace`)\n"
            result_text += "  URL: /lovelace/0\n"
            result_text += "  Mode: storage\n\n"
            
            # Check for additional dashboards
            if isinstance(dashboards_data, dict):
                mode = dashboards_data.get("mode", "storage")
                result_text += f"  Configuration Mode: {mode}\n"
            
            result_text += "\n💡 Use dashboard name in card creation tools"
            
            return [TextContent(type="text", text=result_text)]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error listing dashboards: {str(e)}")]
    
    elif name == "discover_dashboards":
        dashboard_type = arguments.get("dashboard_type", "all")
        include_cards = arguments.get("include_cards", False)
        
        try:
            # Get dashboard configuration
            config = await ha_api.call_api("GET", "lovelace/config", None)
            
            result = {
                "dashboards": [
                    {
                        "id": "lovelace",
                        "title": config.get("title", "Home"),
                        "mode": config.get("mode", "storage"),
                        "url": "/lovelace/0"
                    }
                ],
                "filter": dashboard_type
            }
            
            if include_cards:
                views = config.get("views", [])
                card_count = sum(len(v.get("cards", [])) for v in views)
                result["dashboards"][0]["card_count"] = card_count
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error discovering dashboards: {str(e)}")]
    
    # =================================================================
    # HACS CARDS
    # =================================================================
    
    elif name == "list_hacs_cards":
        try:
            # Get Lovelace resources (custom cards)
            resources = await ha_api.call_api("GET", "lovelace/resources", None)
            
            result_text = "📦 **Installed HACS Custom Cards:**\n\n"
            
            if resources:
                for resource in resources:
                    url = resource.get("url", "")
                    res_type = resource.get("type", "module")
                    
                    # Extract card name from URL
                    card_name = "Unknown"
                    if "button-card" in url:
                        card_name = "button-card"
                    elif "mushroom" in url:
                        card_name = "mushroom"
                    elif "mini-graph-card" in url:
                        card_name = "mini-graph-card"
                    elif "stack-in-card" in url:
                        card_name = "stack-in-card"
                    elif "layout-card" in url:
                        card_name = "layout-card"
                    
                    result_text += f"• **{card_name}** ({res_type})\n"
                    result_text += f"  URL: {url}\n\n"
            else:
                result_text += "No custom cards installed via HACS.\n\n"
                result_text += "💡 Install cards from HACS → Frontend\n"
            
            result_text += "\n🎨 **Popular HACS Cards:**\n"
            result_text += "• button-card - Highly customizable buttons\n"
            result_text += "• mushroom - Modern minimalist design\n"
            result_text += "• mini-graph-card - Compact graphs\n"
            
            return [TextContent(type="text", text=result_text)]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error listing HACS cards: {str(e)}")]
    
    elif name == "create_button_card":
        dashboard = arguments.get("dashboard", "lovelace")
        entity_id = arguments.get("entity_id")
        name = arguments.get("name")
        icon = arguments.get("icon")
        color = arguments.get("color", "auto")
        tap_action = arguments.get("tap_action", "toggle")
        show_state = arguments.get("show_state", True)
        show_name = arguments.get("show_name", True)
        
        try:
            # Get current dashboard config
            config = await ha_api.call_api("GET", "lovelace/config", None)
            
            # Create button-card configuration
            button_card = {
                "type": "custom:button-card",
                "entity": entity_id,
                "color": color,
                "tap_action": {"action": tap_action}
            }
            
            if name:
                button_card["name"] = name
            if icon:
                button_card["icon"] = icon
            if not show_state:
                button_card["show_state"] = False
            if not show_name:
                button_card["show_name"] = False
            
            # Add to first view (or create one)
            if "views" not in config or not config["views"]:
                config["views"] = [{"title": "Home", "cards": []}]
            
            config["views"][0]["cards"].append(button_card)
            
            # Update dashboard
            await ha_api.call_api("POST", "lovelace/config", config)
            
            return [TextContent(type="text", text=(
                f"✅ **Button Card Created!**\n\n"
                f"🎨 Entity: `{entity_id}`\n"
                f"📝 Name: {name or 'Auto'}\n"
                f"🎨 Color: {color}\n"
                f"🖱️ Tap Action: {tap_action}\n\n"
                f"💡 Card added to dashboard: {dashboard}\n"
                f"Refresh your dashboard to see the new button!"
            ))]
        except Exception as e:
            if "404" in str(e):
                return [TextContent(type="text", text=(
                    f"❌ Dashboard '{dashboard}' not found.\n\n"
                    f"💡 Use list_dashboards() to see available dashboards."
                ))]
            return [TextContent(type="text", text=f"❌ Error creating button card: {str(e)}")]
    
    elif name == "create_mushroom_card":
        dashboard = arguments.get("dashboard", "lovelace")
        card_type = arguments.get("card_type")
        entity_id = arguments.get("entity_id")
        name = arguments.get("name")
        icon = arguments.get("icon")
        fill_container = arguments.get("fill_container", False)
        show_temperature_control = arguments.get("show_temperature_control", True)
        layout = arguments.get("layout", "horizontal")
        
        try:
            # Get current dashboard config
            config = await ha_api.call_api("GET", "lovelace/config", None)
            
            # Create mushroom card configuration
            mushroom_card = {
                "type": f"custom:mushroom-{card_type}-card",
                "entity": entity_id,
                "layout": layout,
                "fill_container": fill_container
            }
            
            if name:
                mushroom_card["name"] = name
            if icon:
                mushroom_card["icon"] = icon
            
            # Card-type specific options
            if card_type == "climate" and not show_temperature_control:
                mushroom_card["collapsible_controls"] = True
            
            # Add to first view
            if "views" not in config or not config["views"]:
                config["views"] = [{"title": "Home", "cards": []}]
            
            config["views"][0]["cards"].append(mushroom_card)
            
            # Update dashboard
            await ha_api.call_api("POST", "lovelace/config", config)
            
            return [TextContent(type="text", text=(
                f"✅ **Mushroom Card Created!**\n\n"
                f"🍄 Type: {card_type}\n"
                f"🎯 Entity: `{entity_id}`\n"
                f"📐 Layout: {layout}\n"
                f"📦 Fill Container: {fill_container}\n\n"
                f"💡 Card added to dashboard: {dashboard}\n"
                f"Refresh your dashboard to see the new mushroom card!"
            ))]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error creating mushroom card: {str(e)}")]
    
    # =================================================================
    # STANDARD CARDS
    # =================================================================
    
    elif name == "create_dashboard_card":
        dashboard = arguments.get("dashboard", "lovelace")
        card_type = arguments.get("card_type")
        entity = arguments.get("entity")
        entities = arguments.get("entities", [])
        title = arguments.get("title")
        name = arguments.get("name")
        icon = arguments.get("icon")
        min_val = arguments.get("min")
        max_val = arguments.get("max")
        
        try:
            # Get current dashboard config
            config = await ha_api.call_api("GET", "lovelace/config", None)
            
            # Create card configuration
            card = {"type": card_type}
            
            if entity:
                card["entity"] = entity
            if entities:
                card["entities"] = entities
            if title:
                card["title"] = title
            if name:
                card["name"] = name
            if icon:
                card["icon"] = icon
            if min_val is not None:
                card["min"] = min_val
            if max_val is not None:
                card["max"] = max_val
            
            # Add to first view
            if "views" not in config or not config["views"]:
                config["views"] = [{"title": "Home", "cards": []}]
            
            config["views"][0]["cards"].append(card)
            
            # Update dashboard
            await ha_api.call_api("POST", "lovelace/config", config)
            
            return [TextContent(type="text", text=(
                f"✅ **Dashboard Card Created!**\n\n"
                f"📋 Type: {card_type}\n"
                f"🎯 Entity: {entity or 'Multiple' if entities else 'None'}\n"
                f"📝 Title: {title or 'Auto'}\n\n"
                f"💡 Card added to dashboard: {dashboard}\n"
                f"Refresh your dashboard to see the new card!"
            ))]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error creating dashboard card: {str(e)}")]
    
    # =================================================================
    # CARD EDITING & DELETION
    # =================================================================
    
    elif name == "edit_dashboard_card":
        dashboard = arguments.get("dashboard", "lovelace")
        card_index = arguments.get("card_index")
        
        try:
            # Get current dashboard config
            config = await ha_api.call_api("GET", "lovelace/config", None)
            
            # Validate card index
            if "views" not in config or not config["views"]:
                return [TextContent(type="text", text="❌ Dashboard has no views")]
            
            cards = config["views"][0].get("cards", [])
            if card_index >= len(cards):
                return [TextContent(type="text", text=(
                    f"❌ Card index {card_index} not found.\n"
                    f"Dashboard has {len(cards)} cards (indices 0-{len(cards)-1})\n\n"
                    f"💡 Use get_dashboard_config() to see all cards."
                ))]
            
            # Update card properties
            card = cards[card_index]
            
            if "color" in arguments:
                card["color"] = arguments["color"]
            if "icon" in arguments:
                card["icon"] = arguments["icon"]
            if "name" in arguments:
                card["name"] = arguments["name"]
            if "entity_id" in arguments:
                card["entity"] = arguments["entity_id"]
            if "tap_action" in arguments:
                card["tap_action"] = {"action": arguments["tap_action"]}
            if "show_state" in arguments:
                card["show_state"] = arguments["show_state"]
            if "show_name" in arguments:
                card["show_name"] = arguments["show_name"]
            
            # Update dashboard
            await ha_api.call_api("POST", "lovelace/config", config)
            
            updated_props = [f"  • {k}: {v}" for k, v in arguments.items() if k not in ["dashboard", "card_index"]]
            
            return [TextContent(type="text", text=(
                f"✅ **Card Updated!**\n\n"
                f"📍 Card Index: {card_index}\n"
                f"📋 Dashboard: {dashboard}\n\n"
                f"Updated properties:\n" +
                "\n".join(updated_props) +
                "\n\n💡 Refresh your dashboard to see the changes!"
            ))]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error editing card: {str(e)}")]
    
    elif name == "delete_dashboard_card":
        dashboard = arguments.get("dashboard", "lovelace")
        card_index = arguments.get("card_index")
        
        try:
            # Get current dashboard config
            config = await ha_api.call_api("GET", "lovelace/config", None)
            
            # Validate card index
            if "views" not in config or not config["views"]:
                return [TextContent(type="text", text="❌ Dashboard has no views")]
            
            cards = config["views"][0].get("cards", [])
            if card_index >= len(cards):
                return [TextContent(type="text", text=(
                    f"❌ Card index {card_index} not found.\n"
                    f"Dashboard has {len(cards)} cards (indices 0-{len(cards)-1})\n\n"
                    f"💡 Use get_dashboard_config() to see all cards."
                ))]
            
            # Remove card
            deleted_card = cards.pop(card_index)
            
            # Update dashboard
            await ha_api.call_api("POST", "lovelace/config", config)
            
            return [TextContent(type="text", text=(
                f"✅ **Card Deleted!**\n\n"
                f"📍 Card Index: {card_index}\n"
                f"📋 Dashboard: {dashboard}\n"
                f"🗑️ Card Type: {deleted_card.get('type', 'unknown')}\n\n"
                f"💡 Refresh your dashboard to see the changes."
            ))]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error deleting card: {str(e)}")]
    
    # =================================================================
    # DASHBOARD INSPECTION
    # =================================================================
    
    elif name == "get_dashboard_config":
        dashboard = arguments.get("dashboard", "lovelace")
        
        try:
            # Get dashboard config
            config = await ha_api.call_api("GET", "lovelace/config", None)
            
            result_text = f"🔍 **Dashboard Configuration: {dashboard}**\n\n"
            
            # Dashboard info
            result_text += f"**Mode:** {config.get('mode', 'storage')}\n"
            result_text += f"**Title:** {config.get('title', 'Home')}\n\n"
            
            # Views
            views = config.get("views", [])
            result_text += f"**Views:** {len(views)}\n\n"
            
            # Cards in first view
            if views:
                cards = views[0].get("cards", [])
                result_text += f"**Cards in First View:** {len(cards)}\n\n"
                
                if cards:
                    result_text += "**Card Details:**\n"
                    for idx, card in enumerate(cards):
                        card_type = card.get("type", "unknown")
                        entity = card.get("entity", card.get("entities", "N/A"))
                        result_text += f"\n**Card {idx}** (`{card_type}`)\n"
                        
                        if entity != "N/A":
                            if isinstance(entity, list):
                                result_text += f"  Entities: {', '.join(entity[:3])}"
                                if len(entity) > 3:
                                    result_text += f" (+{len(entity)-3} more)"
                                result_text += "\n"
                            else:
                                result_text += f"  Entity: {entity}\n"
                        
                        # Show key properties
                        if "name" in card:
                            result_text += f"  Name: {card['name']}\n"
                        if "color" in card:
                            result_text += f"  Color: {card['color']}\n"
                        if "icon" in card:
                            result_text += f"  Icon: {card['icon']}\n"
            
            return [TextContent(type="text", text=result_text)]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error getting dashboard config: {str(e)}")]
    
    elif name == "get_dashboard_card":
        dashboard_id = arguments.get("dashboard_id", "lovelace")
        card_index = arguments.get("card_index")
        list_all = arguments.get("list_all", False)
        
        try:
            # Get dashboard config
            config = await ha_api.call_api("GET", "lovelace/config", None)
            
            if "views" not in config or not config["views"]:
                return [TextContent(type="text", text="❌ Dashboard has no views")]
            
            cards = config["views"][0].get("cards", [])
            
            if list_all:
                # List all cards with indices
                result_text = f"📋 **All Cards in {dashboard_id}:**\n\n"
                for idx, card in enumerate(cards):
                    card_type = card.get("type", "unknown")
                    entity = card.get("entity", "N/A")
                    result_text += f"**{idx}:** {card_type} - {entity}\n"
                
                return [TextContent(type="text", text=result_text)]
            
            if card_index is None:
                return [TextContent(type="text", text="❌ Provide card_index or set list_all=true")]
            
            if card_index >= len(cards):
                return [TextContent(type="text", text=(
                    f"❌ Card index {card_index} not found.\n"
                    f"Dashboard has {len(cards)} cards."
                ))]
            
            # Get specific card
            card = cards[card_index]
            
            return [TextContent(type="text", text=json.dumps(card, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error getting card: {str(e)}")]
    
    else:
        return None  # Tool not in Part 3
