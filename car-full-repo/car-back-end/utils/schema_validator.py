"""
Schema validation utility for Vehicle Selection V1
"""
import json
import os
from jsonschema import validate, ValidationError, Draft7Validator
from typing import Dict, Any, Tuple, Optional


class VehicleSelectionV1Validator:
    """Validator for Vehicle Selection V1 schema"""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize the validator with the schema
        
        Args:
            schema_path: Optional path to schema file. If None, uses default location.
        """
        if schema_path is None:
            # Default to schemas directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            schema_path = os.path.join(
                os.path.dirname(current_dir),
                "schemas",
                "vehicle_selection_v1_schema.json"
            )
        
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
        
        self.validator = Draft7Validator(self.schema)
    
    def validate(self, instance: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a JSON instance against the Vehicle Selection V1 schema
        
        Args:
            instance: Dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if valid, False otherwise
            - error_message: None if valid, error description if invalid
        """
        try:
            validate(instance=instance, schema=self.schema)
            return True, None
        except ValidationError as e:
            error_path = " -> ".join(str(x) for x in e.path)
            error_msg = f"Validation error at '{error_path}': {e.message}"
            return False, error_msg
    
    def is_valid(self, instance: Dict[str, Any]) -> bool:
        """
        Check if instance is valid (convenience method)
        
        Args:
            instance: Dictionary to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        is_valid, _ = self.validate(instance)
        return is_valid
    
    def get_errors(self, instance: Dict[str, Any]) -> list:
        """
        Get all validation errors for an instance
        
        Args:
            instance: Dictionary to validate
            
        Returns:
            list: List of error messages
        """
        errors = []
        for error in self.validator.iter_errors(instance):
            error_path = " -> ".join(str(x) for x in error.path)
            errors.append(f"'{error_path}': {error.message}")
        return errors

