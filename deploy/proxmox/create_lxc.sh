#!/bin/bash
# Create and start an Agent Zero LXC container on Proxmox

set -e

if [ $# -lt 2 ]; then
  echo "Usage: $0 <VMID> <storage> [bridge=vmbr0]" >&2
  exit 1
fi

VMID=$1
STORAGE=$2
BRIDGE=${3:-vmbr0}

TEMPLATE=local:vztmpl/ubuntu-22.04-standard_20240429.tar.zst
HOSTNAME=agent-zero-$VMID
MEMORY=4096
CORES=2

pct create "$VMID" "$TEMPLATE" \
  --rootfs "$STORAGE":8 \
  --hostname "$HOSTNAME" \
  --memory "$MEMORY" \
  --cores "$CORES" \
  --net0 name=eth0,bridge="$BRIDGE",ip=dhcp

pct start "$VMID"
pct exec "$VMID" -- apt-get update
pct exec "$VMID" -- apt-get install -y docker.io

pct push "$VMID" ../../example.env /root/.agent-zero.env

pct exec "$VMID" -- docker run -d --name agent-zero \
  --env-file /root/.agent-zero.env \
  -p 80:80 frdel/agent-zero-run:latest

echo "Container $VMID created and Agent Zero started."
