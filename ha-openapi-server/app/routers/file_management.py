from fastapi import APIRouter, Body, HTTPException
import re
from app.core.clients import file_mgr
from app.models.common import SuccessResponse
from app.models.files import (
    ReadFileRequest, WriteFileRequest, 
    ListDirectoryRequest, DeleteFileRequest,
    MakeDirectoryRequest, MoveFileRequest, CopyFileRequest,
    SearchFilesRequest, ListFilesRequest, GetDirectoryTreeRequest
)

router = APIRouter(tags=["file_management"])

@router.post("/read_file", operation_id="read_file", summary="Read file content")
async def ha_read_file(request: ReadFileRequest = Body(...)):
    """Read content of a text file from the HA config directory."""
    content = await file_mgr.ha_read_file(request.filepath)
    return SuccessResponse(
        message=f"Read {len(content)} bytes from {request.filepath}",
        data={"content": content, "filepath": request.filepath}
    )

@router.post("/write_file", operation_id="write_file", summary="Write file content")
async def ha_write_file(request: WriteFileRequest = Body(...)):
    """Write content to a file in the HA config directory."""
    result = await file_mgr.ha_write_file(request.filepath, request.content)
    return SuccessResponse(message=result)

@router.post("/list_directory", operation_id="list_directory", summary="List directory contents")
async def ha_list_directory(request: ListDirectoryRequest = Body(...)):
    """List files and directories in a path."""
    items = await file_mgr.ha_list_directory(request.dirpath)
    return SuccessResponse(message=f"Found {len(items)} items in {request.dirpath or 'root'}", data=items)

@router.post("/delete_file", operation_id="delete_file", summary="Delete a file")
async def ha_delete_file(request: DeleteFileRequest = Body(...)):
    """Delete a file from the config directory."""
    result = await file_mgr.ha_delete_file(request.filepath)
    return SuccessResponse(message=result)

@router.post("/make_directory", operation_id="make_directory", summary="Create a directory")
async def ha_make_directory(request: MakeDirectoryRequest = Body(...)):
    """Create a new directory."""
    path = file_mgr.ha_resolve_path(request.dirpath)
    path.mkdir(parents=True, exist_ok=True)
    return SuccessResponse(message=f"Directory created: {request.dirpath}")

@router.post("/move_file", operation_id="move_file", summary="Move or rename a file")
async def ha_move_file(request: MoveFileRequest = Body(...)):
    """Move or rename a file."""
    src = file_mgr.ha_resolve_path(request.source_path)
    dst = file_mgr.ha_resolve_path(request.dest_path)
    
    if not src.exists():
        raise HTTPException(status_code=404, detail=f"Source not found: {request.source_path}")
    if dst.exists():
        raise HTTPException(status_code=400, detail=f"Destination already exists: {request.dest_path}")
        
    src.rename(dst)
    return SuccessResponse(message=f"Moved {request.source_path} to {request.dest_path}")

@router.post("/copy_file", operation_id="copy_file", summary="Copy a file")
async def ha_copy_file(request: CopyFileRequest = Body(...)):
    """Copy a file."""
    import shutil
    src = file_mgr.ha_resolve_path(request.source_path)
    dst = file_mgr.ha_resolve_path(request.dest_path)
    
    if not src.is_file():
        raise HTTPException(status_code=400, detail=f"Source is not a file: {request.source_path}")
        
    shutil.copy2(src, dst)
    return SuccessResponse(message=f"Copied {request.source_path} to {request.dest_path}")

@router.post("/search_files", operation_id="search_files", summary="Search for files")
async def ha_search_files(request: SearchFilesRequest = Body(...)):
    """Search for files using regex or glob patterns."""
    root = file_mgr.ha_resolve_path(request.path)
    
    if not root.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {request.path}")
    if not root.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.path}")
    
    # Try compiling regex
    try:
        regex = re.compile(request.pattern)
    except re.error as e:
        # Fallback to simple glob-style pattern conversion
        # Convert common glob patterns: *.yaml -> .*\.yaml$
        try:
            pattern = request.pattern
            # If it looks like a simple glob (*.ext), convert it
            if pattern.startswith("*.") and pattern.count("*") == 1:
                ext = pattern[2:]  # Remove *.
                pattern = f".*\\.{re.escape(ext)}$"
            else:
                # General glob conversion
                pattern = pattern.replace(".", "\\.").replace("*", ".*")
            regex = re.compile(pattern)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid pattern: {request.pattern} - {str(e)}")

    matches = []
    
    def scan(p):
        try:
            for item in p.iterdir():
                if item.is_file():
                    if regex.search(item.name):
                        matches.append(str(item.relative_to(file_mgr.base_path)).replace("\\", "/"))
                elif item.is_dir() and request.recursive:
                    scan(item)
        except PermissionError:
            pass  # Ignore permission errors
        except Exception as e:
            # Log other errors but continue
            pass
            
    scan(root)
    return SuccessResponse(message=f"Found {len(matches)} matches", data=matches)

@router.post("/list_files", operation_id="list_files", summary="List files with filtering")
async def ha_list_files(request: ListFilesRequest = Body(...)):
    """List files, optionally filtering by extension."""
    root = file_mgr.ha_resolve_path(request.path)
    
    if not root.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {request.path}")
    if not root.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.path}")
    
    matches = []
    # Normalize extensions to lowercase and ensure they start with dot
    extensions = set()
    if request.extensions:
        for ext in request.extensions:
            ext = ext.lower()
            if not ext.startswith("."):
                ext = f".{ext}"
            extensions.add(ext)
    
    def scan(p):
        try:
            for item in p.iterdir():
                if item.is_file():
                    if not extensions or item.suffix.lower() in extensions:
                        matches.append(str(item.relative_to(file_mgr.base_path)).replace("\\", "/"))
                elif item.is_dir() and request.recursive:
                    scan(item)
        except PermissionError:
            pass  # Ignore permission errors
        except Exception:
            pass
            
    scan(root)
    return SuccessResponse(message=f"Found {len(matches)} files", data=matches)

@router.post("/get_directory_tree", operation_id="get_directory_tree", summary="Get directory tree")
async def ha_get_directory_tree(request: GetDirectoryTreeRequest = Body(...)):
    """Get recursive directory structure."""
    root = file_mgr.ha_resolve_path(request.dirpath)
    
    if not root.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {request.dirpath}")
    if not root.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.dirpath}")
    
    def build_tree(p, depth):
        if depth < 0:
            return "..."
        try:
            res = {}
            for item in p.iterdir():
                if item.is_dir():
                    res[item.name] = build_tree(item, depth - 1)
                else:
                    res[item.name] = None
            return res
        except PermissionError:
            return "<Permission Denied>"
        except Exception as e:
            return f"<Error: {e}>"
            
    tree = build_tree(root, request.depth)
    return SuccessResponse(message="Directory tree", data=tree)
