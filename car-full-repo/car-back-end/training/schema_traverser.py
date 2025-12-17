"""
Schema Traverser - Recursively traverses JSON schema to build annotation field list
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class SchemaTraverser:
    """Traverses JSON schema recursively to extract annotation fields"""
    
    def __init__(self, schema_path: Path):
        self.schema_path = Path(schema_path)
        self.schema: Dict[str, Any] = {}
        self.definitions: Dict[str, Any] = {}
        self.fields: List[Dict[str, Any]] = []
    
    def load_schema(self):
        """Load and parse JSON schema file"""
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
        
        # Extract definitions for $ref resolution
        self.definitions = self.schema.get('definitions', {})
    
    def resolve_ref(self, ref: str) -> Dict[str, Any]:
        """
        Resolve a $ref reference
        
        Args:
            ref: Reference string like "#/definitions/body_style"
        
        Returns:
            Resolved schema definition
        """
        if not ref.startswith('#/definitions/'):
            raise ValueError(f"Unsupported $ref format: {ref}")
        
        def_name = ref.replace('#/definitions/', '')
        if def_name not in self.definitions:
            raise ValueError(f"Definition not found: {def_name}")
        
        return self.definitions[def_name]
    
    def get_field_type(self, field_schema: Dict[str, Any]) -> str:
        """Determine the field type from schema"""
        # Handle $ref
        if '$ref' in field_schema:
            ref_schema = self.resolve_ref(field_schema['$ref'])
            return self.get_field_type(ref_schema)
        
        # Check for enum
        if 'enum' in field_schema:
            return 'enum'
        
        # Check type
        field_type = field_schema.get('type')
        if isinstance(field_type, list):
            # Handle nullable types like ["integer", "null"]
            field_type = [t for t in field_type if t != 'null'][0] if field_type else 'string'
        
        return field_type or 'string'
    
    def is_nullable(self, field_schema: Dict[str, Any]) -> bool:
        """Check if field is nullable"""
        field_type = field_schema.get('type')
        if isinstance(field_type, list):
            return 'null' in field_type
        return False
    
    def get_enum_values(self, field_schema: Dict[str, Any]) -> Optional[List[Any]]:
        """Extract enum values from schema, resolving $ref if needed"""
        # Handle $ref
        if '$ref' in field_schema:
            ref_schema = self.resolve_ref(field_schema['$ref'])
            return self.get_enum_values(ref_schema)
        
        # Direct enum
        if 'enum' in field_schema:
            return field_schema['enum']
        
        return None
    
    def traverse(self, schema: Optional[Dict[str, Any]] = None, path: List[str] = None, required_fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        Recursively traverse schema to build flat list of annotation fields
        
        Args:
            schema: Schema to traverse (defaults to root schema)
            path: Current path in schema (e.g., ['vehicle_type', 'include_body_styles'])
            required_fields: List of required field names at current level
        
        Returns:
            List of field definitions for annotation
        """
        if schema is None:
            schema = self.schema
            required_fields = schema.get('required', [])
            path = []
        
        if path is None:
            path = []
        
        if required_fields is None:
            required_fields = []
        
        fields = []
        
        # Handle object type
        if schema.get('type') == 'object' or 'properties' in schema:
            properties = schema.get('properties', {})
            obj_required = schema.get('required', [])
            
            for prop_name, prop_schema in properties.items():
                prop_path = path + [prop_name]
                prop_required = prop_name in obj_required
                
                # Resolve $ref if present
                if '$ref' in prop_schema:
                    prop_schema = self.resolve_ref(prop_schema['$ref'])
                
                # Get field type
                field_type = self.get_field_type(prop_schema)
                
                # Handle arrays
                if field_type == 'array' or prop_schema.get('type') == 'array':
                    items_schema = prop_schema.get('items', {})
                    
                    # Resolve $ref in items
                    if '$ref' in items_schema:
                        items_schema = self.resolve_ref(items_schema['$ref'])
                    
                    item_type = self.get_field_type(items_schema)
                    
                    # Array of enums
                    if item_type == 'enum':
                        enum_values = self.get_enum_values(items_schema)
                        fields.append({
                            'path': prop_path,
                            'name': '.'.join(prop_path),
                            'type': 'array_enum',
                            'enum_values': enum_values,
                            'nullable': self.is_nullable(prop_schema),
                            'required': prop_required
                        })
                    # Array of objects (not common in this schema, but handle it)
                    elif item_type == 'object':
                        # For arrays of objects, we'd need to handle multiple items
                        # For now, treat as single object annotation
                        nested_fields = self.traverse(items_schema, prop_path, items_schema.get('required', []))
                        fields.extend(nested_fields)
                    else:
                        # Array of primitives
                        fields.append({
                            'path': prop_path,
                            'name': '.'.join(prop_path),
                            'type': f'array_{item_type}',
                            'nullable': self.is_nullable(prop_schema),
                            'required': prop_required
                        })
                
                # Handle nested objects
                elif field_type == 'object':
                    nested_required = prop_schema.get('required', [])
                    nested_fields = self.traverse(prop_schema, prop_path, nested_required)
                    fields.extend(nested_fields)
                
                # Handle enums
                elif field_type == 'enum':
                    enum_values = self.get_enum_values(prop_schema)
                    fields.append({
                        'path': prop_path,
                        'name': '.'.join(prop_path),
                        'type': 'enum',
                        'enum_values': enum_values,
                        'nullable': self.is_nullable(prop_schema),
                        'required': prop_required
                    })
                
                # Handle primitives (string, number, integer, boolean)
                else:
                    fields.append({
                        'path': prop_path,
                        'name': '.'.join(prop_path),
                        'type': field_type,
                        'nullable': self.is_nullable(prop_schema),
                        'required': prop_required
                    })
        
        return fields
    
    def get_fields(self) -> List[Dict[str, Any]]:
        """Load schema and return flat list of annotation fields"""
        self.load_schema()
        self.fields = self.traverse()
        return self.fields


