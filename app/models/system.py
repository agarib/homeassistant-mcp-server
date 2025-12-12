from typing import Optional
from pydantic import BaseModel, Field

# ============================================================================
# System
# ============================================================================

class RestartHomeAssistantRequest(BaseModel):
    confirm: bool = Field(..., description="Must be true to confirm restart")

# ============================================================================
# Add-ons
# ============================================================================

class ListAddonsRequest(BaseModel):
    installed_only: Optional[bool] = Field(True, description="Only show installed add-ons")

class ControlAddonRequest(BaseModel):
    addon_slug: str = Field(..., description="Add-on slug identifier")
    action: str = Field(..., description="Action: start, stop, restart, install, uninstall")

class GetAddonStatsRequest(BaseModel):
    addon_slug: str = Field(..., description="Add-on slug identifier")

# ============================================================================
# System Diagnostics
# ============================================================================

class GetSystemLogsNewRequest(BaseModel):
    lines: Optional[int] = Field(100, ge=1, le=10000, description="Number of lines to retrieve")
    level: Optional[str] = Field(None, description="Filter by log level: 'ERROR', 'WARNING', 'INFO', 'DEBUG'")

class GetIntegrationStatusNewRequest(BaseModel):
    integration: Optional[str] = Field(None, description="Specific integration to check")

# ============================================================================
# Diagnostics
# ============================================================================

class GetConfigEntryDiagnosticsRequest(BaseModel):
    entry_id: str = Field(..., description="Config entry ID from /api/config/config_entries")
    integration: Optional[str] = Field(None, description="Integration name (optional, for filtering)")

class GetDeviceDiagnosticsRequest(BaseModel):
    device_id: str = Field(..., description="Device ID from /api/config/device_registry/list")

class ListAvailableDiagnosticsRequest(BaseModel):
    integration_filter: Optional[str] = Field(None, description="Filter by integration name")
