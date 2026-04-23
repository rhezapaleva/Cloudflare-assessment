#!/bin/bash
set -e

echo "==> Downloading cloudflared..."
curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared
echo "==> cloudflared installed: $(cloudflared --version)"

echo "==> Starting Cloudflare Tunnel..."
cloudflared tunnel run --token $TUNNEL_TOKEN &
TUNNEL_PID=$!
echo "==> Tunnel started with PID $TUNNEL_PID"

echo "==> Starting Gunicorn on port $PORT..."
gunicorn app:app --bind 0.0.0.0:$PORT