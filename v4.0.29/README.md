# Home Assistant OpenAPI Server v4.0.29

Modular, production-ready FastAPI server for Home Assistant integration. Designed for use with Open-WebUI and Cloud AI agents.

## Features
- **97 Unified Endpoints**: Full control over devices, automations, and file system.
- **WebSocket & REST**: Hybrid architecture for real-time dashboard control and robust API access.
- **AI-Ready**: Consistent `ha_` naming convention and optimized parameter handling (snake_case/camelCase support).
- **Modular Architecture**: Easy to maintain and extend.

## Installation
```bash
pip install -r requirements.txt
```

## Running
```bash
python -m app.main
```
Server will be available at http://0.0.0.0:8001

## Documentation
- API Docs: http://0.0.0.0:8001/docs
- AI Guide: [README_AI.md](README_AI.md)
