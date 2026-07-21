from typing import List, Optional
from pydantic import BaseModel, Field

# ============================================================================
# File Management Request Models
# ============================================================================

class ReadFileRequest(BaseModel):
    filepath: str = Field(..., description="Path to the file to read")

class WriteFileRequest(BaseModel):
    filepath: str = Field(..., description="Path to the file to write")
    content: str = Field(..., description="Content to write to the file")

class ListDirectoryRequest(BaseModel):
    dirpath: str = Field(..., description="Directory path to list")

class DeleteFileRequest(BaseModel):
    filepath: str = Field(..., description="Path to the file to delete")

class MakeDirectoryRequest(BaseModel):
    dirpath: str = Field(..., description="Directory path to create")

class MoveFileRequest(BaseModel):
    source_path: str = Field(..., description="Source file path")
    dest_path: str = Field(..., description="Destination file path")

class CopyFileRequest(BaseModel):
    source_path: str = Field(..., description="Source file path")
    dest_path: str = Field(..., description="Destination file path")

class SearchFilesRequest(BaseModel):
    path: str = Field(..., description="Root directory to search")
    pattern: str = Field(..., description="Regex pattern to search for")
    recursive: bool = Field(default=True, description="Search recursively")

class ListFilesRequest(BaseModel):
    path: str = Field(..., description="Directory to list files from")
    extensions: Optional[List[str]] = Field(default=None, description="Filter by file extensions")
    recursive: bool = Field(default=True, description="List recursively")

class GetDirectoryTreeRequest(BaseModel):
    dirpath: str = Field("", description="Directory to get tree for")
    depth: Optional[int] = Field(default=None, description="Maximum depth to traverse")