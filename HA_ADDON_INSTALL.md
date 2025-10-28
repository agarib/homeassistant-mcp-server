Installation & Deployment Guide — ha-mcp-server add-on

## Overview

This folder `ha-mcp-server-addon` contains the Home Assistant add-on package for the MCP server. The add-on runs inside Home Assistant and exposes an HTTP/SSE MCP server on port 8001.

## Files of interest

- `config.json` — Add-on metadata (already present)
- `run.sh` — Add‑on entrypoint (calls `python3 -u server.py`)
- `requirements.txt` — Python dependencies
- `server.py` — MCP server implementation (the file we edited/added)

## Quick install steps (Home Assistant supervisor)

1. Copy the folder `ha-mcp-server-addon` to your Home Assistant add-ons custom repository (on the machine running Supervisor) or place it into a local add-on store directory.

2. If using the local add-on folder on the Supervisor host (example path: `/usr/share/hassio/addons/local/`):

```powershell
# On the Supervisor host (example commands)
# Copy the add-on folder into the local add-on directory (requires host access)
scp -r C:\MyProjects\ha-mcp-server-addon root@homeassistant-host:/usr/share/hassio/addons/local/
```

3. In Home Assistant UI → Supervisor → Add-on Store → (3-dot menu) → Repositories → Add your local repository if necessary, then install `ha-mcp-server` add-on.

4. Configure and start the add-on. The add-on will use the Supervisor token to call the Supervisor/HA API:

- `HA_URL` should be `http://supervisor/core/api` (already set by `run.sh`)
- `HA_TOKEN` is auto-provided via `SUPERVISOR_TOKEN` environment in Supervisor-managed add-ons

5. After starting the add-on, verify it listens on port 8001 inside the Supervisor network. If you have `host` networking enabled for Supervisor add-ons, use the host IP and port 8001 to reach it from outside.

## MCPO integration (cluster)

MCPO (running in your k8s cluster on worker-one) must reach the add-on's `/messages` SSE endpoint (used as the MCP transport) and, optionally, the other HTTP endpoints we added:

- SSE transport: `http://<ha-host>:8001/messages` (the MCPO mcpServers mapping already used `http://192.168.1.203:8001/messages` in `mcpo-config-updated.yaml`)
- Extra endpoints we added: `/subscribe_events`, `/api/state`, `/api/actions`, `/api/actions/batch`

If MCPO is outside the HA host network, ensure the HA host IP (`192.168.1.203` in your MCPO config) is reachable from the cluster network. If not, set up routing or expose the add-on service via an ingress or local port-forward.

## Updating MCPO config & rolling restart (k8s)

If you need to update the MCPO ConfigMap to change the homeassistant URL, edit `mcpo-config-updated.yaml` and apply it:

```powershell
kubectl apply -f C:\MyProjects\mcpo-config-updated.yaml -n cluster-services
# Then restart mcpo-server pods to pick up changes
kubectl rollout restart statefulset mcpo-server -n cluster-services
kubectl get pods -n cluster-services -w
```

## Troubleshooting

- If the add-on fails to start, view Supervisor logs for the add-on and the `run.sh` output in the UI.
- Verify the add-on container has Python 3.10+ and can `pip install` dependencies if required.
- If MCPO cannot connect to the SSE endpoint, test connectivity from a pod inside the cluster (e.g., `kubectl run --rm -it --image=curlimages/curl tmp -- curl -v http://192.168.1.203:8001/messages`).

## Security notes

- Do not commit real tokens or secrets to git. The `SUPERVISOR_TOKEN` is provided by HA supervisor at runtime; do not hardcode values.

If you want, I can:

- Update `mcpo-config-updated.yaml` to change the HA URL to a different host or hostname
- Create a Kubernetes Service that exposes the HA add-on (if HA is also running in-cluster)
- Generate a pre-built Docker add-on image (if you prefer image-based add-on)

What next would you like me to do? (Pick one)

1. Update `mcpo-config-updated.yaml` (change the homeassistant URL or add an HTTP proxy route)
2. Create a Kubernetes Service / ingress manifest to expose the add-on to the cluster
3. Help prepare a Docker-based add-on image and show how to install it
4. Start integration testing instructions (SSE, VLM, batch actions)
