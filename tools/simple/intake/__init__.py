"""
Intake Module for SimpleTool

This module handles request processing and field access for SimpleTool.
Extracted from tools/simple/base.py as part of Phase 2 Cleanup refactoring.

Responsibilities:
- Safe request field access
- Request attribute extraction
- Default value handling
"""

from tools.simple.intake.accessor import RequestAccessor

__all__ = ["RequestAccessor"]

