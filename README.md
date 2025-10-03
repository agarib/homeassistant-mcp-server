# Home Assistant MCP Server

**Authors:** GitHub Copilot and agarib
**Version:** 1.0.0
**License:** MIT
**Date:** October 4, 2025

A comprehensive Model Context Protocol (MCP) server for Home Assistant with 60 tools including SSH/SFTP file management.

## Features

- **60 Intelligent Tools** (55 HA controls + 5 file management)
- **SSH/SFTP Integration** for /config directory access
- **Production k3s Deployment** ready
- **YAML Validation** for safe file operations
- **Automatic Backups** (.bak and .deleted files)

## Installation

See docs/DEPLOYMENT_GUIDE.md for complete installation instructions.

## Configuration

Required environment variables:

```yaml
HA_URL: "http://your-ha-instance:8123"
HA_TOKEN: "your-long-lived-access-token"
HA_SSH_HOST: "your-ha-instance"
HA_SSH_PORT: "22"
HA_SSH_USER: "root"
HA_SSH_PASSWORD: "your-ssh-password"
```

## Documentation

- Installation Guide: docs/DEPLOYMENT_GUIDE.md
- File Management: docs/FILE_MANAGEMENT.md
- Cluster Setup: docs/CLUSTER_SETUP.md

## License

MIT License - see LICENSE file

---

**Made with â¤ï¸ by GitHub Copilot and agarib**