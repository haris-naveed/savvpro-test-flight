"""ASGI entrypoint when running uvicorn from the repository root."""

from backend.main import app

__all__ = ["app"]
