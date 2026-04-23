#!/bin/bash
set -e

echo "==> Downloading cloudflared..."
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared
echo "==> cloudflared installed: $(cloudflared --version)"

echo "==> Starting Cloudflare Tunnel..."
cloudflared tunnel run --token $TUNNEL_TOKEN &

echo "==> Starting Gunicorn on port $PORT..."
exec gunicorn app:app --bind 0.0.0.0:$PORT