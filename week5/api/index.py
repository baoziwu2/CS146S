"""
Vercel serverless entry point.

Vercel's Python runtime detects the `app` ASGI object and wraps it automatically.
The week5/ project root is added to sys.path so `backend` is importable.
"""

import os
import sys

# Ensure the week5/ root (parent of this api/ dir) is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.main import app  # noqa: F401, E402 — re-exported for Vercel
