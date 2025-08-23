"""
IntelliOS Storage Module

This module contains data persistence components:
- Vector database operations for semantic search
- PostgreSQL client for structured data
- Cache management for performance
"""

from .vector_db import VectorDBManager

__all__ = ['VectorDBManager']
