#!/bin/bash
set -euo pipefail

# Install dependencies
sudo apt-get update
sudo apt-get install -y git python3 python3-venv python3-pip nginx

# Clone repository
sudo mkdir -p /opt/agent-zero
sudo chown "$USER" /opt/agent-zero
if [ ! -d /opt/agent-zero/.git ]; then
    git clone https://github.com/cloudcurio/agent-zero.git /opt/agent-zero
fi
cd /opt/agent-zero

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/agent-zero.service >/dev/null <<'SERVICE'
[Unit]
Description=Agent Zero Service
After=network.target

[Service]
Type=simple
User=%i
WorkingDirectory=/opt/agent-zero
ExecStart=/opt/agent-zero/venv/bin/python3 run_ui.py
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable agent-zero.service
sudo systemctl start agent-zero.service

# Configure Nginx
sudo tee /etc/nginx/sites-available/agent-zero.conf >/dev/null <<'NGINX'
server {
    listen 80;
    server_name cloudcurio.cc;
    location /agent-zero/ {
        proxy_pass http://127.0.0.1:50001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/agent-zero.conf /etc/nginx/sites-enabled/agent-zero.conf
sudo nginx -s reload

echo "Deployment complete. Visit http://cloudcurio.cc/agent-zero" 
