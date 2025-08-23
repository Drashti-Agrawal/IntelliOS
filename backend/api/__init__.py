"""
IntelliOS API Module

This module contains the REST API components:
- FastAPI server for external communication
- API routes and endpoints
- Request/response middleware
- Input validation
"""

from .server import app

__all__ = ['app']
