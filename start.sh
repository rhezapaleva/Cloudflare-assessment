#!/bin/bash
set -e

echo "==> Downloading cloudflared using Python..."
python3 -c "
import urllib.request
url = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64'
urllib.request.urlretrieve(url, '/usr/local/bin/cloudflared')
print('Download complete')
"
chmod +x /usr/local/bin/cloudflared
echo "==> cloudflared installed: $(cloudflared --version)"

# Use Railway's PORT, default to 8080 if not set
APP_PORT=${PORT:-8080}
echo "==> App port is $APP_PORT"

echo "==> Starting Cloudflare Tunnel pointing to localhost:$APP_PORT..."
cloudflared tunnel run --token $TUNNEL_TOKEN --url http://localhost:$APP_PORT &

echo "==> Starting Gunicorn on port $APP_PORT..."
exec gunicorn app:app --bind 0.0.0.0:$APP_PORT