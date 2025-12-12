from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel

class SuccessResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Union[Dict[str, Any], List[Any]]] = None

class ErrorResponse(BaseModel):
    status: str = "error"
    error: str
    details: Optional[str] = None
