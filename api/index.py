"""
api/index.py - Vercel Serverless Function Entry Point for CineMatch AI
Exposes Flask WSGI application instance `app` (and `handler`) for Vercel's serverless runtime.
Includes WSGI path translation middleware to normalize Vercel rewrite URLs.
"""

import os
import sys

# Ensure repository root is on sys.path so app and recommender can be imported cleanly
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app


class VercelPathFixMiddleware:
    """
    Normalizes WSGI PATH_INFO when Vercel serverless functions rewrite all
    incoming traffic (/(.*) -> /api/index). Restores the client's original requested
    path using Vercel routing headers or by stripping the function prefix.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # 1. Check if Vercel provided the client's original requested path in headers
        client_path = (
            environ.get("HTTP_X_MATCHED_PATH")
            or environ.get("HTTP_X_FORWARDED_URI")
            or environ.get("HTTP_X_VERCEL_PATH")
        )

        if client_path and not client_path.startswith("/api/index"):
            clean_path = client_path.split("?")[0]
            environ["PATH_INFO"] = clean_path
        else:
            # 2. If Vercel rewrote the path to /api/index (or /api/index/...), strip the prefix
            path_info = environ.get("PATH_INFO", "")
            if path_info.startswith("/api/index"):
                clean_path = path_info[len("/api/index"):]
                if not clean_path.startswith("/"):
                    clean_path = "/" + clean_path
                environ["PATH_INFO"] = clean_path

        # 3. Always ensure a valid non-empty path
        if not environ.get("PATH_INFO"):
            environ["PATH_INFO"] = "/"

        return self.wsgi_app(environ, start_response)


# Wrap Flask with Vercel path correction middleware
app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)

# Vercel serverless WSGI entrypoint
handler = app
