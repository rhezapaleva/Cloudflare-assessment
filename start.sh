#!/bin/bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Start tunnel in background
cloudflared tunnel run --token eyJhIjoiNGZkM2JmMWFjMTczNGI3YWJjYzdhZTdmMDc1NjhjNmUiLCJ0IjoiNWYyYTIwYTYtZTUwYi00ZmE2LWFhZTUtYTJiOTJkYjcyYjNiIiwicyI6IlpETmpOekZqTUdNdE5XWmxOaTAwTmpjekxXSTFOamt0TXpZMU1UQmtOell4WmpZNCJ9 &

# Start Flask app
gunicorn app:app --bind 0.0.0.0:$PORT