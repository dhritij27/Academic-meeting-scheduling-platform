import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Local imports
from db import ping_db

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.get("/db/ping")
def db_ping():
    ok = ping_db()
    return jsonify({"ok": ok}), (200 if ok else 500)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
