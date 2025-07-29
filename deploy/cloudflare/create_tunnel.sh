#!/usr/bin/env bash
set -euo pipefail

# Creates and configures a Cloudflare Tunnel for Agent Zero
# Requires the cloudflared CLI installed and authenticated.

TUNNEL_NAME=${TUNNEL_NAME:-agent-zero}
DOMAIN=${DOMAIN:-cloud-curio.cc}
SUBDOMAIN=${SUBDOMAIN:-a0}
AGENT_PORT=${AGENT_PORT:-50001}

cloudflared tunnel login

if ! cloudflared tunnel list | awk '{print $1}' | grep -q "^${TUNNEL_NAME}$"; then
    cloudflared tunnel create "${TUNNEL_NAME}"
fi

cloudflared tunnel route dns "${TUNNEL_NAME}" "${SUBDOMAIN}.${DOMAIN}"

CONFIG_DIR="${HOME}/.cloudflared"
mkdir -p "${CONFIG_DIR}"
TUNNEL_ID=$(cloudflared tunnel list | awk -v name="${TUNNEL_NAME}" '$1==name {print $2}')

cat > "${CONFIG_DIR}/${TUNNEL_NAME}.yaml" <<CFG
tunnel: ${TUNNEL_ID}
credentials-file: ${CONFIG_DIR}/${TUNNEL_ID}.json
ingress:
  - service: http://localhost:${AGENT_PORT}
  - service: http_status:404
CFG

cat <<MSG
Tunnel created. To start it run:
cloudflared tunnel --config ${CONFIG_DIR}/${TUNNEL_NAME}.yaml run
MSG

