# Quick Reference - ha_list_files Tool

## Overview

The `ha_list_files` tool lists all files in a directory with optional filtering by extension and recursive search.

---

## Endpoint

```
POST http://192.168.1.203:8001/ha_list_files
```

---

## Parameters

| Parameter    | Type    | Required | Default | Description                                           |
| ------------ | ------- | -------- | ------- | ----------------------------------------------------- |
| `directory`  | string  | Yes      | `"."`   | Directory to list files from (relative to `/config`)  |
| `extensions` | array   | No       | `null`  | File extensions to filter by (e.g., `["yaml", "py"]`) |
| `recursive`  | boolean | No       | `false` | Search subdirectories recursively                     |

---

## Examples

### List all YAML files in root config

```json
{
  "directory": ".",
  "extensions": ["yaml"],
  "recursive": false
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Found 7 files in .",
  "data": {
    "files": [
      {
        "name": "automations.yaml",
        "path": "automations.yaml",
        "size": 412,
        "extension": "yaml"
      },
      {
        "name": "configuration.yaml",
        "path": "configuration.yaml",
        "size": 1217,
        "extension": "yaml"
      }
    ],
    "count": 7
  }
}
```

---

### Recursively list Python files in custom_components

```json
{
  "directory": "custom_components",
  "extensions": ["py"],
  "recursive": true
}
```

---

### List all files in packages (no filtering)

```json
{
  "directory": "packages",
  "recursive": false
}
```

---

### Find all JSON and YAML files recursively

```json
{
  "directory": ".",
  "extensions": ["json", "yaml"],
  "recursive": true
}
```

---

## PowerShell Test Commands

```powershell
# List YAML files in root
$body = '{"directory":".","extensions":["yaml"],"recursive":false}'
Invoke-RestMethod -Uri "http://192.168.1.203:8001/ha_list_files" -Method POST -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 3

# List all files in automations folder
$body = '{"directory":"automations","recursive":false}'
Invoke-RestMethod -Uri "http://192.168.1.203:8001/ha_list_files" -Method POST -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 3

# Recursively find all Python files
$body = '{"directory":"custom_components","extensions":["py"],"recursive":true}'
Invoke-RestMethod -Uri "http://192.168.1.203:8001/ha_list_files" -Method POST -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 3
```

---

## Use Cases

1. **Find configuration files**: List all YAML files in a specific package
2. **Audit custom components**: Find all Python files recursively
3. **Check automation files**: List automations directory contents
4. **File management**: See what files exist before reading/writing
5. **Debug missing files**: Verify file locations and extensions

---

## Related Tools

- **ha_read_file**: Read file contents after listing
- **ha_write_file**: Create/update files
- **ha_list_directory**: List both files and directories with detailed info
- **ha_search_files**: Search files by content pattern
- **ha_get_directory_tree**: Get hierarchical directory structure

---

## Notes

- All paths are relative to `/config` directory
- Security: Cannot list files outside `/config`
- Empty results: Returns `count: 0` with empty files array
- Large directories: Consider using `extensions` filter to reduce results

---

**Added in Version:** 4.0.10  
**Status:** ✅ Production Ready
