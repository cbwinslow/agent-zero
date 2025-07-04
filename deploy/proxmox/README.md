# Deploying Agent Zero on Proxmox

This guide explains how to launch Agent Zero in an LXC container on a Proxmox server.

## Prerequisites
- A running Proxmox VE host with access to an Ubuntu template (e.g. `ubuntu-22.04`)
- Sufficient privileges to create containers
- Internet access from the Proxmox host to pull Docker images

## Steps
1. **Download a base template**
   ```bash
   pveam update
   pveam download local ubuntu-22.04-standard_20240429
   ```
2. **Create the container**
   ```bash
   ./create_lxc.sh <VMID> <storage>
   ```
   Replace `<VMID>` with an unused ID and `<storage>` with the storage target (for example `local-lvm`).
3. **Configure API endpoints**
   After creation the script installs Docker and launches the Agent Zero container. Edit the `.env` file inside the container to point to your API endpoints:
   ```bash
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   OPEN_ROUTER_BASE_URL=https://openrouter.ai/api/v1
   # add any other endpoints here
   ```
4. **Access the Web UI**
   By default port `80` of the container is exposed. Navigate to `http://<container_ip>` to open Agent Zero.

## MCP Servers
If you run separate MCP servers, add them through the settings UI after the first launch or edit `tmp/settings.json` in the container.

