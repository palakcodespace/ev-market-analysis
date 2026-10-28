"""
WSGI Production Entrypoint for Electric Vehicle Market Intelligence System.
Suitable for Gunicorn (Linux/Docker/Render/Railway) and Waitress (Windows).
"""
import os
import sys
from pathlib import Path

# Ensure root directory is in python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    if os.name == "nt":
        # Windows Production WSGI using Waitress
        try:
            from waitress import serve
            print(f"Starting Waitress production server on http://127.0.0.1:{port}...")
            serve(app, host="0.0.0.0", port=port)
        except ImportError:
            print("Waitress not installed. Running Flask development server...")
            app.run(host="0.0.0.0", port=port)
    else:
        # Linux / Unix fallback
        app.run(host="0.0.0.0", port=port)
