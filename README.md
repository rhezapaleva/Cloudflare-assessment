# Rheza's Guestbook — Cloudflare Assessment

A Flask guestbook app serving as the origin server for the Cloudflare Associate SE take-home assessment.

## Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | / | Public guestbook — view messages + submission form |
| POST | /message | Submit a new guestbook message |
| GET | /secure | Admin area (protected by Cloudflare Zero Trust + Worker) |
| GET | /health | Health check (JSON) |

## Local development

```bash
pip install -r requirements.txt
python app.py
```

App runs on http://localhost:5000

## Deploy to Railway

1. Push this repo to GitHub
2. Go to railway.app → New Project → Deploy from GitHub repo
3. Select this repo — Railway detects the Procfile automatically
4. Settings → Networking → Generate Domain to get your public URL

## Architecture

```
User → Cloudflare (WAF + Rate Limit + TLS) → Cloudflare Tunnel → Flask app (Railway)
                                                      ↓
                                          /secure intercepted by CF Worker
                                                      ↓
                                          Worker reads flags from R2 / D1
```
