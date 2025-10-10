"""
Schema Generation for SimpleTool

This module provides schema generation functionality for SimpleTool.
Extracted from tools/simple/base.py as part of Phase 2 Cleanup refactoring.

The SimpleToolSchemaBuilder class handles:
- Input schema generation using SchemaBuilder
- Common field definitions (FILES_FIELD, IMAGES_FIELD)
- Integration with tool-specific fields
- Auto-mode model field handling
"""

from typing import Any


class SimpleToolSchemaBuilder:
    """
    Schema generation for SimpleTool.
    
    This class provides static methods and constants for building
    JSON schemas for SimpleTool instances. It delegates to the shared
    SchemaBuilder while providing SimpleTool-specific conveniences.
    """
    
    # Common field definitions that simple tools can reuse
    # These are convenience references to SchemaBuilder constants
    # for backward compatibility with existing code
    
    @staticmethod
    def get_files_field() -> dict[str, Any]:
        """
        Get the FILES field schema definition.
        
        Returns:
            dict: JSON schema for the files field
        """
        from tools.shared.schema_builders import SchemaBuilder
        return SchemaBuilder.SIMPLE_FIELD_SCHEMAS["files"]
    
    @staticmethod
    def get_images_field() -> dict[str, Any]:
        """
        Get the IMAGES field schema definition.
        
        Returns:
            dict: JSON schema for the images field
        """
        from tools.shared.schema_builders import SchemaBuilder
        return SchemaBuilder.COMMON_FIELD_SCHEMAS["images"]
    
    # Class-level properties for backward compatibility
    # These allow SimpleTool.FILES_FIELD and SimpleTool.IMAGES_FIELD to work
    @property
    def FILES_FIELD(self) -> dict[str, Any]:
        """Backward compatibility property for FILES_FIELD"""
        return self.get_files_field()
    
    @property
    def IMAGES_FIELD(self) -> dict[str, Any]:
        """Backward compatibility property for IMAGES_FIELD"""
        return self.get_images_field()
    
    @staticmethod
    def build_input_schema(tool_instance) -> dict[str, Any]:
        """
        Build complete input schema for a SimpleTool instance.
        
        This method generates the full JSON schema for a SimpleTool by:
        1. Getting tool-specific fields from get_tool_fields()
        2. Getting required fields from get_required_fields()
        3. Getting model field schema from get_model_field_schema()
        4. Checking auto mode status from is_effective_auto_mode()
        5. Delegating to SchemaBuilder.build_schema()
        
        Args:
            tool_instance: The SimpleTool instance to build schema for
            
        Returns:
            dict: Complete JSON schema for the tool
            
        Example:
            >>> from tools.chat import ChatTool
            >>> tool = ChatTool()
            >>> schema = SimpleToolSchemaBuilder.build_input_schema(tool)
            >>> assert "properties" in schema
            >>> assert "prompt" in schema["properties"]
        """
        from tools.shared.schema_builders import SchemaBuilder
        
        return SchemaBuilder.build_schema(
            tool_specific_fields=tool_instance.get_tool_fields(),
            required_fields=tool_instance.get_required_fields(),
            model_field_schema=tool_instance.get_model_field_schema(),
            auto_mode=tool_instance.is_effective_auto_mode(),
        )
    
    @staticmethod
    def validate_schema(schema: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate a generated schema for correctness.
        
        This is a helper method for testing and debugging schema generation.
        It checks that the schema has the required structure and fields.
        
        Args:
            schema: The schema to validate
            
        Returns:
            tuple: (is_valid, list_of_errors)
            
        Example:
            >>> schema = {"type": "object", "properties": {}, "required": []}
            >>> is_valid, errors = SimpleToolSchemaBuilder.validate_schema(schema)
            >>> assert is_valid
        """
        errors = []
        
        # Check required top-level fields
        if not isinstance(schema, dict):
            errors.append("Schema must be a dictionary")
            return False, errors
        
        if schema.get("type") != "object":
            errors.append("Schema type must be 'object'")
        
        if "properties" not in schema:
            errors.append("Schema must have 'properties' field")
        
        if not isinstance(schema.get("properties"), dict):
            errors.append("Schema properties must be a dictionary")
        
        # Check that required is a list if present
        if "required" in schema and not isinstance(schema["required"], list):
            errors.append("Schema required must be a list")
        
        return len(errors) == 0, errors

