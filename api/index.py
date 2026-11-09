"""Vercel entry point: the whole FastAPI app as one Python function (Doc3 section 15, G0)."""
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.main import app  # noqa: F401
