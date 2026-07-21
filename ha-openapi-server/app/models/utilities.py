from typing import Optional, Any
from pydantic import BaseModel, Field

class EvalTemplateRequest(BaseModel):
    template: str = Field(..., description="Jinja2 template to render")

class ConfigSetYamlRequest(BaseModel):
    file_path: str = Field(..., description="Relative path from config dir (e.g., configuration.yaml, packages/foo.yaml)")
    yaml_key: str = Field(..., description="Top-level YAML key to modify")
    action: str = Field("merge", description="Action: merge, replace, or remove")
    content: Any = Field(..., description="Content to merge/replace")
    confirm: bool = Field(False, description="Must be true to confirm modification")
