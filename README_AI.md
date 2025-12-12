# 🤖 Cloud AI Integration Guide

**Version:** 4.0.29  
**Target Audience:** Claude, ChatGPT, Gemini, and other AI Agents using this toolset.

## 🎯 Core Directive
You are controlling a Home Assistant instance via the `ha-openapi-server`.  
**ALWAYS** use the tools provided with the `ha_` prefix.

## 🛠️ Tool Categories

### 1. Device Control
Use these tools to control physical devices.
- `ha_control_light`: Turn on/off, brightness, color.
- `ha_control_switch`: Toggle plugs, relays.
- `ha_control_climate`: Set temperature, HVAC mode.
- `ha_control_cover`: Open/close blinds, garage.

**Example (Light):**
```json
{
  "entity_id": "light.living_room",
  "action": "turn_on",
  "brightness": 255
}
```

### 2. Information & Discovery
- `ha_list_devices`: See all devices.
- `ha_get_states`: Check status of entities.
- `ha_get_system_logs_diagnostics`: Debug issues if something fails.

### 3. File Operations
Full access to `/config` directory.
- `ha_read_file` / `ha_write_file`: Edit configuration YAMLs.
- `ha_list_directory`: Explore the file system.

**Compatible Parameters:**
You can use either `filepath` (legacy) or `file_path` (snake_case). Both work!

### 4. Special Capabilities
- **Automations**: Use `ha_reload_automations` after editing YAML files. No restart needed!
- **Dashboards**: Use `ha_get_dashboard_config` to see Lovelace config.

## 💡 Pro Tips for AI Agents
1. **Always check state first**: Before toggling a switch, use `ha_get_entity_state` to see if it's already on.
2. **Handle Errors**: If a tool fails, use `ha_get_system_logs_diagnostics` to read the error log.
3. **Paths**: File paths are relative to `/config`. E.g., `configuration.yaml`, not `/config/configuration.yaml`.
