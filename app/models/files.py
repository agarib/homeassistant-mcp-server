from typing import Optional
from pydantic import BaseModel, Field

class ReadFileRequest(BaseModel):
    model_config = {"populate_by_name": True}
    
    filepath: str = Field(..., description="Path relative to /config", alias="file_path")

class WriteFileRequest(BaseModel):
    # Support both naming conventions for compatibility
    filepath: str = Field(..., description="Path relative to /config", validation_alias="file_path")
    content: str = Field(..., description="File content to write")

class ListDirectoryRequest(BaseModel):
    model_config = {"populate_by_name": True}
    
    dirpath: str = Field("", description="Directory path relative to /config", alias="dir_path")

class DeleteFileRequest(BaseModel):
    model_config = {"populate_by_name": True}
    
    filepath: str = Field(..., description="File path to delete", alias="file_path")

class MoveFileRequest(BaseModel):
    model_config = {"populate_by_name": True}

    source_path: str = Field(..., description="Source file path")
    dest_path: str = Field(..., description="Destination file path")

class CopyFileRequest(BaseModel):
    model_config = {"populate_by_name": True}

    source_path: str = Field(..., description="Source file path")
    dest_path: str = Field(..., description="Destination file path")

class MakeDirectoryRequest(BaseModel):
    model_config = {"populate_by_name": True}

    dirpath: str = Field(..., description="Directory path to create", alias="dir_path")

class SearchFilesRequest(BaseModel):
    pattern: str = Field(..., description="Regex pattern to search for (e.g., '*.yaml')")
    path: str = Field(".", description="Starting directory path")
    recursive: bool = Field(True, description="Search recursively")

class ListFilesRequest(BaseModel):
    path: str = Field(".", description="Directory path")
    extensions: Optional[list] = Field(None, description="Filter by extensions (e.g., ['.yaml', '.json'])")
    recursive: bool = Field(False, description="List recursively")

class GetDirectoryTreeRequest(BaseModel):
    model_config = {"populate_by_name": True}
    
    dirpath: str = Field("", description="Root directory path", alias="dir_path")
    depth: int = Field(2, description="Maximum recursion depth")
