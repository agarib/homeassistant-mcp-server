from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# ============================================================================
# Dashboards (Lovelace)
# ============================================================================

class GetDashboardConfigRequest(BaseModel):
    dashboard_id: str = Field(..., description="Dashboard ID (e.g., 'lovelace' for default)")

class UpdateDashboardConfigRequest(BaseModel):
    dashboard_id: str = Field(..., description="Dashboard ID")
    config: Dict[str, Any] = Field(..., description="Full Dashboard configuration object")

class ListDashboardsRequest(BaseModel):
    pass

class CreateDashboardRequest(BaseModel):
    url_path: str = Field(..., description="URL path for dashboard (e.g. 'custom-dashboard')")
    title: str = Field(..., description="Dashboard title")
    icon: Optional[str] = Field(None, description="Dashboard icon")
    require_admin: bool = Field(False, description="Require admin access")

class DeleteDashboardRequest(BaseModel):
    dashboard_id: str = Field(..., description="Dashboard ID to delete")

# ============================================================================
# Cards
# ============================================================================

class ManualCreateCustomCardRequest(BaseModel):
    dashboard_id: str = Field(..., description="Dashboard ID (e.g., 'lovelace' for default)")
    view_index: int = Field(..., description="View/tab index (0-based)")
    card_yaml: str = Field(..., description="Card configuration as YAML string")
    position: Optional[int] = Field(None, description="Card position in view (0-based, default: append)")

class ManualEditCustomCardRequest(BaseModel):
    dashboard_id: str = Field(..., description="Dashboard ID")
    view_index: int = Field(..., description="View/tab index (0-based)")
    card_index: int = Field(..., description="Card index within view (0-based)")
    card_yaml: str = Field(..., description="Updated card configuration as YAML string")

class CreateWeatherCardRequest(BaseModel):
    dashboard_id: str = Field(..., description="Dashboard ID")
    view_index: int = Field(..., description="View index")
    entity_id: str = Field(..., description="Weather entity ID")
    name: Optional[str] = Field(None, description="Card title")

class CreateGaugeCardRequest(BaseModel):
    dashboard_id: str = Field(..., description="Dashboard ID")
    view_index: int = Field(..., description="View index")
    entity_id: str = Field(..., description="Sensor entity ID")
    min: float = 0
    max: float = 100
    name: Optional[str] = Field(None, description="Card title")
    severity: Optional[Dict[str, float]] = Field(None, description="Severity map (green, yellow, red)")
