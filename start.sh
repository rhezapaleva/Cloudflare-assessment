#!/bin/bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared
cloudflared tunnel run --token $TUNNEL_TOKEN &
gunicorn app:app --bind 0.0.0.0:$PORT