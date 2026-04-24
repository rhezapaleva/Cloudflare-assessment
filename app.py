from flask import Flask, request, jsonify, redirect
from datetime import datetime
import os
import sqlite3

app = Flask(__name__)

CF_SECRET = os.environ.get("CF_SECRET", "rheza-secret-2026")

@app.before_request
def check_cf_secret():
    # Allow health checks
    if request.path == "/health":
        return
    # Allow if correct secret header present (added by Cloudflare Transform Rule)
    secret = request.headers.get("X-Origin-Secret")
    if secret == CF_SECRET:
        return
    # Allow tunnel traffic (protected by Zero Trust Access instead)
    host = request.headers.get("Host", "")
    if "tunnel.rhezapaleva.org" in host:
        return
    # Block everything else (direct Railway access)
    return "Access denied — direct access is not allowed. Please use rhezapaleva.org", 403

DB_PATH = os.environ.get("DB_PATH", "/tmp/guestbook.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            country TEXT DEFAULT '??',
            timestamp TEXT NOT NULL
        )
    """)
    # Seed with demo messages if empty
    count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    if count == 0:
        conn.execute("INSERT INTO messages (name, message, country, timestamp) VALUES (?, ?, ?, ?)",
            ("Alice", "What a lovely guestbook! Really clean design.", "SG", "2026-04-20 10:12:00 UTC"))
        conn.execute("INSERT INTO messages (name, message, country, timestamp) VALUES (?, ?, ?, ?)",
            ("Bob", "Great site, keep it up!", "US", "2026-04-21 14:33:00 UTC"))
        conn.commit()
    conn.close()

init_db()

HOME_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rheza's Guestbook</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f8f7f4;
      color: #1a1a1a;
      min-height: 100vh;
      padding: 2rem 1rem;
    }}
    .container {{ max-width: 680px; margin: 0 auto; }}
    header {{ text-align: center; margin-bottom: 3rem; }}
    header .emoji {{ font-size: 3rem; margin-bottom: 0.5rem; }}
    header h1 {{ font-size: 2rem; font-weight: 700; color: #1a1a1a; }}
    header p {{ color: #666; margin-top: 0.3rem; font-size: 0.95rem; }}
    .card {{
      background: white;
      border: 1px solid #e8e5e0;
      border-radius: 16px;
      padding: 1.75rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }}
    .card h2 {{
      font-size: 1rem;
      font-weight: 600;
      color: #1a1a1a;
      margin-bottom: 1.25rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px solid #f0ede8;
    }}
    .form-group {{ margin-bottom: 1rem; }}
    label {{
      display: block;
      font-size: 0.85rem;
      font-weight: 500;
      color: #444;
      margin-bottom: 0.35rem;
    }}
    input[type=text], textarea {{
      width: 100%;
      padding: 0.65rem 0.9rem;
      border: 1px solid #ddd;
      border-radius: 10px;
      font-size: 0.95rem;
      font-family: inherit;
      background: #fafafa;
      color: #1a1a1a;
      transition: border-color 0.15s, box-shadow 0.15s;
      outline: none;
    }}
    input[type=text]:focus, textarea:focus {{
      border-color: #f6821f;
      box-shadow: 0 0 0 3px rgba(246,130,31,0.12);
      background: white;
    }}
    textarea {{ resize: vertical; min-height: 90px; }}
    button[type=submit] {{
      background: #f6821f;
      color: white;
      border: none;
      padding: 0.7rem 1.75rem;
      border-radius: 10px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.15s, transform 0.1s;
    }}
    button[type=submit]:hover {{ background: #e07010; }}
    button[type=submit]:active {{ transform: scale(0.98); }}
    .flash {{
      padding: 0.75rem 1rem;
      border-radius: 10px;
      margin-bottom: 1rem;
      font-size: 0.9rem;
      font-weight: 500;
    }}
    .flash.success {{ background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }}
    .flash.error   {{ background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }}
    .messages-list {{ display: flex; flex-direction: column; gap: 1rem; }}
    .message-item {{
      background: #fafaf8;
      border: 1px solid #ede9e3;
      border-radius: 12px;
      padding: 1.1rem 1.25rem;
    }}
    .message-header {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      margin-bottom: 0.5rem;
    }}
    .avatar {{
      width: 34px; height: 34px;
      background: linear-gradient(135deg, #f6821f, #fbbf24);
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      color: white; font-weight: 700; font-size: 0.85rem;
      flex-shrink: 0;
    }}
    .message-meta {{ flex: 1; }}
    .message-name {{ font-weight: 600; font-size: 0.9rem; color: #1a1a1a; }}
    .message-time {{ font-size: 0.75rem; color: #999; margin-top: 0.1rem; }}
    .message-text {{ font-size: 0.9rem; color: #444; line-height: 1.6; }}
    .message-country {{
      font-size: 0.75rem;
      background: #f0ede8;
      color: #666;
      padding: 0.15rem 0.5rem;
      border-radius: 999px;
      flex-shrink: 0;
    }}
    .empty {{
      text-align: center;
      padding: 2rem;
      color: #aaa;
      font-size: 0.9rem;
    }}
    footer {{
      text-align: center;
      margin-top: 2rem;
      font-size: 0.8rem;
      color: #bbb;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="emoji">📖</div>
      <h1>Rheza's Guestbook</h1>
      <p>Leave a message — say hello from wherever you are!</p>
    </header>

    {flash}

    <div class="card">
      <h2>✍️ Leave a message</h2>
      <form method="POST" action="/message">
        <div class="form-group">
          <label for="name">Your name</label>
          <input type="text" id="name" name="name" placeholder="e.g. Jane Doe" required maxlength="80">
        </div>
        <div class="form-group">
          <label for="message">Your message</label>
          <textarea id="message" name="message" placeholder="Say something nice..." required maxlength="500"></textarea>
        </div>
        <button type="submit">Post message →</button>
      </form>
    </div>

    <div class="card">
      <h2>💬 Messages ({count})</h2>
      {messages_html}
    </div>

    <footer>Protected by Cloudflare &nbsp;·&nbsp; <a href="/secure" style="color:#f6821f;text-decoration:none;">Admin</a></footer>
  </div>
</body>
</html>"""

SECURE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin — Rheza's Guestbook</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0f1117; color: #e2e8f0;
      min-height: 100vh; display: flex; align-items: center;
      justify-content: center; padding: 2rem;
    }}
    .card {{
      background: #1a1d2e; border: 1px solid #2d3148;
      border-radius: 16px; padding: 2.5rem;
      max-width: 480px; width: 100%; text-align: center;
    }}
    .icon {{ font-size: 2.5rem; margin-bottom: 1rem; }}
    h1 {{ font-size: 1.5rem; font-weight: 700; color: #f6821f; margin-bottom: 0.5rem; }}
    p {{ color: #94a3b8; font-size: 0.95rem; line-height: 1.6; }}
    .badge {{
      display: inline-block; margin-top: 1.5rem;
      background: #f6821f22; border: 1px solid #f6821f55;
      color: #f6821f; padding: 0.35rem 1rem;
      border-radius: 999px; font-size: 0.8rem;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">🔐</div>
    <h1>Admin area</h1>
    <p>This page is protected by Cloudflare Zero Trust.<br>
    Only authorised users can access this area.</p>
    <div class="badge">⚡ Secured by Cloudflare Access</div>
  </div>
</body>
</html>"""


def render_messages():
    conn = get_db()
    rows = conn.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    conn.close()

    if not rows:
        return '<div class="empty">No messages yet — be the first to say hello!</div>'

    html = '<div class="messages-list">'
    for m in rows:
        initial = m["name"][0].upper()
        html += f"""
        <div class="message-item">
          <div class="message-header">
            <div class="avatar">{initial}</div>
            <div class="message-meta">
              <div class="message-name">{m['name']}</div>
              <div class="message-time">{m['timestamp']}</div>
            </div>
            <span class="message-country">{m['country']}</span>
          </div>
          <div class="message-text">{m['message']}</div>
        </div>"""
    html += '</div>'
    return html


@app.route("/")
def index():
    flash = ""
    status = request.args.get("status")
    if status == "ok":
        flash = '<div class="flash success">✓ Message posted successfully!</div>'
    elif status == "err":
        flash = '<div class="flash error">✗ Name and message are required.</div>'

    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    conn.close()

    return HOME_HTML.format(
        flash=flash,
        count=count,
        messages_html=render_messages()
    )


@app.route("/message", methods=["POST"])
def post_message():
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not message:
        return redirect("/?status=err")

    # Sanitise basic HTML to prevent XSS
    name = name.replace("<", "&lt;").replace(">", "&gt;")
    message = message.replace("<", "&lt;").replace(">", "&gt;")

    country = request.headers.get("CF-IPCountry", "??")
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    conn = get_db()
    conn.execute(
        "INSERT INTO messages (name, message, country, timestamp) VALUES (?, ?, ?, ?)",
        (name, message, country, timestamp)
    )
    conn.commit()
    conn.close()

    return redirect("/?status=ok")


@app.route("/secure")
def secure():
    return SECURE_HTML


@app.route("/health")
def health():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    conn.close()
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "message_count": count,
        "database": "sqlite"
    })

@app.route("/debug-headers")
def debug_headers():
    headers = dict(request.headers)
    return jsonify(headers)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)