# Fix Summary: Registry Endpoints (Areas, Devices)

## Problem

The endpoints `ha_list_areas` and `ha_list_devices` were returning `404 Not Found`.
Investigation revealed that these endpoints were attempting to access the Home Assistant Supervisor REST API at `http://supervisor/core/api/config/area_registry/list` and `http://supervisor/core/api/config/device_registry/list`.
These paths do not exist in the standard Home Assistant REST API. Registry access is primarily available via WebSocket or internal integration APIs.

## Solution

The `server.py` was updated to use the `HomeAssistantWebSocket` client for these specific endpoints, while keeping other endpoints on the REST API.

### Changes in `server.py` (v4.0.28)

1. **`ha_list_areas`**:

   - **Old**: `await ha_api.call_api("GET", "config/area_registry/list")` (REST)
   - **New**: `await ws_client.call_command("config/area_registry/list")` (WebSocket)

2. **`ha_list_devices`**:

   - **Old**: `await ha_api.call_api("GET", "config/device_registry/list")` (REST)
   - **New**: `await ws_client.call_command("config/device_registry/list")` (WebSocket)

3. **`ha_list_entities`**:
   - Verified as working correctly using the standard REST API (`/api/states`).

## Verification

- **Deployment**: Updated `server.py` was deployed to `192.168.1.203`.
- **Tests**:
  - `ha_list_areas`: Returns 10 areas (Success).
  - `ha_list_devices`: Returns 126 devices (Success).
  - `ha_list_entities`: Returns 683 entities (Success).
  - `ha_get_services`: Returns service domains (Success).

## Status

All requested endpoints are now fully functional.
