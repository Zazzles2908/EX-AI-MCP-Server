"""
Definition Module for SimpleTool

This module handles tool contract and schema generation for SimpleTool.
Extracted from tools/simple/base.py as part of Phase 2 Cleanup refactoring.

Responsibilities:
- Schema generation and validation
- Field definition management
- Tool contract specification
"""

from tools.simple.definition.schema import SimpleToolSchemaBuilder

__all__ = ["SimpleToolSchemaBuilder"]

