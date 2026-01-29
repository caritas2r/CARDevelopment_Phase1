"""
JSON Input Converter Service - Converts JSON query structure to SQL
"""
from typing import Dict, Any, List, Tuple, Optional
from utils.schema_validator import VehicleSelectionV1Validator


# Declarative mappings for inclusion criteria (priority order matters)
INCLUSION_MAPPINGS = [
    # Priority 1: Identity Fields (Highest selectivity)
    {
        'name': 'make',
        'path': ['make'],
        'type': 'array',
        'sql_field': 'make',
        'operator': 'IN',
        'priority': 1
    },
    {
        'name': 'model',
        'path': ['model'],
        'type': 'array',
        'sql_field': 'model',
        'operator': 'IN',
        'priority': 1
    },
    {
        'name': 'trim',
        'path': ['trim'],
        'type': 'string',
        'sql_field': 'trim',
        'operator': '=',
        'priority': 1
    },
    {
        'name': 'year_min',
        'path': ['ownership_constraints', 'year', 'min'],
        'type': 'number',
        'sql_field': 'year',
        'operator': '>=',
        'priority': 1
    },
    {
        'name': 'year_max',
        'path': ['ownership_constraints', 'year', 'max'],
        'type': 'number',
        'sql_field': 'year',
        'operator': '<=',
        'priority': 1
    },
    
    # Priority 2: Ownership Constraints
    {
        'name': 'mileage_max',
        'path': ['ownership_constraints', 'mileage', 'max'],
        'type': 'number',
        'sql_field': 'mileage',
        'operator': '<=',
        'priority': 2
    },
    {
        'name': 'number_of_owners',
        'path': ['ownership_constraints', 'number_of_owners'],
        'type': 'number',
        'sql_field': 'number_of_owners',
        'operator': '<=',  # Maximum
        'priority': 2
    },
    
    # Priority 3: Body Style Inclusion
    {
        'name': 'include_body_styles',
        'path': ['vehicle_type', 'include_body_styles'],
        'type': 'array',
        'sql_field': 'body_style',
        'operator': 'IN',
        'priority': 3
    },
    
    # Priority 4: Budget
    {
        'name': 'budget_min',
        'path': ['ownership_constraints', 'budget', 'min'],
        'type': 'number',
        'sql_field': 'price',
        'operator': '>=',
        'priority': 4
    },
    # budget_max + strict_max = custom handler (handled separately)
    
    # Direct enum mappings
    {
        'name': 'transmission',
        'path': ['powertrain_drivability', 'transmission'],
        'type': 'enum',
        'sql_field': 'transmission',
        'operator': '=',
        'priority': 5
    },
    {
        'name': 'drivetrain',
        'path': ['powertrain_drivability', 'drivetrain'],
        'type': 'enum',
        'sql_field': 'drivetrain',
        'operator': '=',
        'priority': 5
    },
    
    # Array enum mappings
    {
        'name': 'color',
        'path': ['preference_signals', 'color'],
        'type': 'array',
        'sql_field': 'color',
        'operator': 'IN',
        'priority': 6
    },
    
    # Capacity/Practicality
    {
        'name': 'min_seating_capacity',
        'path': ['capacity_practicality', 'min_seating_capacity'],
        'type': 'number',
        'sql_field': 'seating_capacity',
        'operator': '>=',
        'priority': 6
    },
    
    # Location
    {
        'name': 'city',
        'path': ['location_constraints', 'city'],
        'type': 'string',
        'sql_field': 'city',
        'operator': '=',
        'priority': 7
    },
    {
        'name': 'state_region',
        'path': ['location_constraints', 'state_region'],
        'type': 'string',
        'sql_field': 'state_region',
        'operator': '=',
        'priority': 7
    },
    
    # Enum mappings with transforms
    {
        'name': 'cargo_priority',
        'path': ['capacity_practicality', 'cargo_priority'],
        'type': 'enum_transform',
        'sql_field': 'cargo_space',
        'operator': '=',
        'transform': 'priority_to_level',  # Maps "low"/"medium"/"high" directly
        'priority': 6
    },
    {
        'name': 'fuel_economy_priority',
        'path': ['powertrain_drivability', 'fuel_economy_priority'],
        'type': 'enum_transform',
        'sql_field': 'fuel_economy',
        'operator': '=',
        'transform': 'priority_to_level',  # Maps "low"/"medium"/"high" directly
        'priority': 5
    },
    {
        'name': 'reliability_maintenance_priority',
        'path': ['preference_signals', 'reliability_maintenance_priority'],
        'type': 'enum_transform',
        'sql_field': 'reliability',
        'operator': '=',
        'transform': 'maintenance_priority_to_reliability',  # Maps "low_cost"→"low", "balanced"→"medium", etc.
        'priority': 6
    },
    
    # Junction table mappings (require EXISTS subqueries)
    {
        'name': 'must_have_features',
        'path': ['features_amenities', 'must_have'],
        'type': 'junction',
        'junction_table': 'vehicle_features',
        'junction_field': 'feature_tag',
        'priority': 5
    },
    {
        'name': 'powertrain_types',
        'path': ['powertrain_drivability', 'powertrain_type'],
        'type': 'junction',
        'junction_table': 'vehicle_powertrain_types',
        'junction_field': 'powertrain_type',
        'priority': 5
    },
    {
        'name': 'use_case_tags',
        'path': ['intended_use', 'use_case_tags'],
        'type': 'junction',
        'junction_table': 'vehicle_use_case_tags',
        'junction_field': 'use_case_tag',
        'priority': 6
    },
    
    # TODO: Boolean fields (wants_hatch_access, wants_fold_flat_seats)
    # These should only add conditions when value is "true"
    # {
    #     'name': 'wants_hatch_access',
    #     'path': ['capacity_practicality', 'cargo_flexibility', 'wants_hatch_access'],
    #     'type': 'boolean',
    #     'sql_field': 'has_hatch_access',
    #     'operator': '=',
    #     'priority': 6
    # },
    # {
    #     'name': 'wants_fold_flat_seats',
    #     'path': ['capacity_practicality', 'cargo_flexibility', 'wants_fold_flat_seats'],
    #     'type': 'boolean',
    #     'sql_field': 'has_fold_flat_seats',
    #     'operator': '=',
    #     'priority': 6
    # },
]

# Exclusion mappings
EXCLUSION_MAPPINGS = [
    {
        'name': 'exclude_body_styles',
        'path': ['vehicle_type', 'exclude_body_styles'],
        'type': 'array',
        'sql_field': 'body_style',
        'operator': 'NOT IN',
        'priority': 1
    },
    {
        'name': 'avoid_features',
        'path': ['features_amenities', 'avoid'],
        'type': 'junction_exclude',
        'junction_table': 'vehicle_features',
        'junction_field': 'feature_tag',
        'priority': 1
    },
]


class JsonInputConverterService:
    """Service responsible for converting JSON query structures to SQL"""
    
    def __init__(self):
        """Initialize the JSON input converter service"""
        self.name = "json-input-converter-service"
        self.initialized = False
        self.validator = VehicleSelectionV1Validator()
    
    def register(self, app):
        """
        Register routes and functionality with the Flask app
        
        Args:
            app: Flask application instance
        """
        # No routes needed - this service provides conversion methods
        pass
    
    def initialize(self):
        """Initialize the service"""
        if not self.initialized:
            print(f"[{self.name}] Initializing...")
            # Add initialization logic here
            self.initialized = True
            print(f"[{self.name}] Initialized successfully")
    
    def convert_to_sql(self, json_structure):
        """
        Convert JSON query structure to SQL query string using two-phase approach:
        1. Build inclusion criteria (WHERE conditions)
        2. Build exclusion criteria (AND NOT conditions)
        
        Args:
            json_structure: Dictionary containing Vehicle Selection V1 JSON structure
        
        Returns:
            Tuple[str, List[Any]]: SQL query string and parameter values
        
        Raises:
            ValueError: If JSON structure is invalid or query is inconclusive (no conditions)
        """
        # Phase 1: Build inclusion criteria
        inclusion_conditions, inclusion_params = self._build_inclusion_conditions(json_structure)
        
        # Phase 2: Build exclusion criteria
        exclusion_conditions, exclusion_params = self._build_exclusion_conditions(json_structure)
        
        # Combine conditions
        all_conditions = inclusion_conditions + exclusion_conditions
        all_params = inclusion_params + exclusion_params
        
        # Validate that we have at least one condition
        if not all_conditions:
            raise ValueError("Inconclusive search results, please refine your query criteria.")
        
        # Build final query
        where_clause = "WHERE " + " AND ".join(all_conditions)
        query = f"SELECT * FROM vehicles {where_clause}"
        return query, all_params
    
    def _build_inclusion_conditions(self, json_data: Dict[str, Any]) -> Tuple[List[str], List[Any]]:
        """Build inclusion WHERE conditions from mappings"""
        conditions = []
        params = []
        
        # Sort mappings by priority
        sorted_mappings = sorted(INCLUSION_MAPPINGS, key=lambda x: x['priority'])
        
        for mapping in sorted_mappings:
            condition, param_values = self._build_condition_from_mapping(mapping, json_data)
            if condition:
                conditions.append(condition)
                params.extend(param_values)
        
        # Handle custom handlers (budget_max + strict_max)
        budget_condition, budget_params = self._build_budget_max_condition(json_data)
        if budget_condition:
            conditions.append(budget_condition)
            params.extend(budget_params)
        
        return conditions, params
    
    def _build_exclusion_conditions(self, json_data: Dict[str, Any]) -> Tuple[List[str], List[Any]]:
        """Build exclusion WHERE conditions from mappings"""
        conditions = []
        params = []
        
        # Sort mappings by priority
        sorted_mappings = sorted(EXCLUSION_MAPPINGS, key=lambda x: x['priority'])
        
        for mapping in sorted_mappings:
            condition, param_values = self._build_condition_from_mapping(mapping, json_data)
            if condition:
                conditions.append(condition)
                params.extend(param_values)
        
        return conditions, params
    
    def _build_condition_from_mapping(self, mapping: Dict[str, Any], json_data: Dict[str, Any]) -> Tuple[Optional[str], List[Any]]:
        """
        Build a single WHERE condition from a mapping definition
        
        Args:
            mapping: Mapping definition dictionary
            json_data: JSON data to extract values from
        
        Returns:
            Tuple[Optional[str], List[Any]]: Condition string and parameter values, or (None, []) if no condition
        """
        # Extract value using path
        value = self._extract_path(json_data, mapping['path'])
        
        if value is None:
            return None, []
        
        # Handle different mapping types
        mapping_type = mapping['type']
        
        # Junction table mappings (EXISTS subqueries) - treat as arrays for filtering
        if mapping_type in ['junction', 'junction_exclude']:
            # Filter out "unspecified" from junction table arrays
            value = self._filter_and_convert_value(value, 'array')
            if value is None or len(value) == 0:
                return None, []
            include = (mapping_type == 'junction')
            return self._build_junction_condition(mapping, value, include=include)
        
        # Filter out "unspecified" and validate/convert types for other mappings
        value = self._filter_and_convert_value(value, mapping_type)
        
        if value is None or (isinstance(value, list) and len(value) == 0):
            return None, []
        
        # Enum mappings with transforms
        if mapping_type == 'enum_transform':
            transformed_value = self._apply_enum_transform(value, mapping.get('transform'))
            if transformed_value is None:
                return None, []
            condition = f"{mapping['sql_field']} {mapping['operator']} %s"
            return condition, [transformed_value]
        
        # Standard mappings
        sql_field = mapping['sql_field']
        operator = mapping['operator']
        
        if mapping_type == 'array' and operator in ['IN', 'NOT IN']:
            placeholders = ','.join(['%s'] * len(value))
            condition = f"{sql_field} {operator} ({placeholders})"
            return condition, value
        
        elif mapping_type in ['number', 'enum', 'string']:
            condition = f"{sql_field} {operator} %s"
            return condition, [value]
        
        return None, []
    
    def _extract_path(self, json_data: Dict[str, Any], path: List[str]) -> Any:
        """
        Extract value from JSON using nested path (e.g., ['ownership_constraints', 'year', 'min'])
        
        Args:
            json_data: JSON dictionary
            path: List of keys representing the path
        
        Returns:
            Extracted value or None if path doesn't exist
        """
        current = json_data
        for key in path:
            if not isinstance(current, dict):
                return None
            current = current.get(key)
            if current is None:
                return None
        return current
    
    def _filter_and_convert_value(self, value: Any, value_type: str) -> Any:
        """
        Filter out "unspecified" values and convert types
        
        Args:
            value: Raw value from JSON
            value_type: Expected type ('array', 'number', 'enum', 'string', 'boolean')
        
        Returns:
            Filtered/converted value, or None if should be skipped
        """
        # Handle arrays
        if value_type == 'array':
            if not isinstance(value, list):
                return None
            # Filter out "unspecified" (case-insensitive)
            filtered = [v for v in value if not (isinstance(v, str) and v.lower() == "unspecified")]
            return filtered if filtered else None
        
        # Handle single values - normalize to lowercase for comparison
        if isinstance(value, str):
            value_lower = value.lower()
            if value_lower == "unspecified":
                return None
        elif value is None:
            return None
        
        # Type conversion/validation
        if value_type == 'number':
            # Convert string numbers to int/float
            if isinstance(value, str):
                try:
                    # Try integer first, then float
                    if '.' in value:
                        return float(value)
                    return int(value)
                except ValueError:
                    return None
            if isinstance(value, (int, float)):
                return value
            return None
        
        elif value_type == 'boolean':
            # Convert string booleans to actual booleans
            if isinstance(value, str):
                if value.lower() in ('true', '1', 'yes'):
                    return 1
                elif value.lower() in ('false', '0', 'no'):
                    return 0
                return None
            if isinstance(value, bool):
                return 1 if value else 0
            if isinstance(value, int):
                return 1 if value != 0 else 0
            return None
        
        elif value_type in ['enum', 'string']:
            # For enum/string, just return as-is (validation happens at schema level)
            if isinstance(value, str):
                return value
            # Convert other types to string if needed
            return str(value) if value is not None else None
        
        return value
    
    def _build_junction_condition(self, mapping: Dict[str, Any], value: List[str], include: bool = True) -> Tuple[Optional[str], List[Any]]:
        """
        Build junction table condition using EXISTS subquery
        
        Args:
            mapping: Mapping definition with junction_table and junction_field
            value: List of values to match
            include: True for inclusion (EXISTS), False for exclusion (NOT EXISTS)
        
        Returns:
            Tuple[Optional[str], List[Any]]: Condition string and parameter values
        """
        if not value or len(value) == 0:
            return None, []
        
        junction_table = mapping['junction_table']
        junction_field = mapping['junction_field']
        
        placeholders = ','.join(['%s'] * len(value))
        
        if include:
            # Inclusion: EXISTS (SELECT 1 FROM junction_table WHERE vehicle_id = vehicles.vehicle_id AND field IN (...))
            condition = (
                f"EXISTS (SELECT 1 FROM {junction_table} jt "
                f"WHERE jt.vehicle_id = vehicles.vehicle_id "
                f"AND jt.{junction_field} IN ({placeholders}))"
            )
        else:
            # Exclusion: NOT EXISTS (SELECT 1 FROM junction_table WHERE vehicle_id = vehicles.vehicle_id AND field IN (...))
            condition = (
                f"NOT EXISTS (SELECT 1 FROM {junction_table} jt "
                f"WHERE jt.vehicle_id = vehicles.vehicle_id "
                f"AND jt.{junction_field} IN ({placeholders}))"
            )
        
        return condition, value
    
    def _apply_enum_transform(self, value: str, transform_type: Optional[str]) -> Optional[str]:
        """
        Apply enum transformation based on transform type
        
        Args:
            value: Enum value from JSON
            transform_type: Type of transform ('priority_to_level', 'maintenance_priority_to_reliability')
        
        Returns:
            Transformed value or None if should be skipped
        """
        if value is None:
            return None
        
        # Normalize to lowercase for comparison
        if isinstance(value, str):
            value_lower = value.lower()
            if value_lower == "unspecified":
                return None
        else:
            value_lower = str(value).lower()
        
        if transform_type == 'priority_to_level':
            # Direct mapping: "low" → "low", "medium" → "medium", "high" → "high", "unspecified" → None
            if value_lower in ['low', 'medium', 'high']:
                return value_lower  # Return normalized lowercase value
            return None
        
        elif transform_type == 'maintenance_priority_to_reliability':
            # Maps maintenance priority to reliability level (normalized to lowercase)
            # "unspecified" → None (handled at function start)
            mapping = {
                'low_cost': 'low',
                'balanced': 'medium',
                'performance_first': 'high',
                'luxury_ok': 'high'
            }
            return mapping.get(value_lower)
        
        # Unknown transform type - return normalized value as-is
        return value_lower if isinstance(value_lower, str) else None
    
    def _build_budget_max_condition(self, json_data: Dict[str, Any]) -> Tuple[Optional[str], List[Any]]:
        """
        Build budget.max condition with strict_max logic (custom handler)
        
        If strict_max is "true": price <= budget.max
        If strict_max is not "true": price <= (budget.max * 1.1)  # 10% flexibility
        """
        budget = json_data.get('ownership_constraints', {}).get('budget', {})
        budget_max = budget.get('max')
        strict_max = budget.get('strict_max')
        
        # Check for unspecified (case-insensitive)
        if budget_max is None or (isinstance(budget_max, str) and budget_max.lower() == "unspecified"):
            return None, []
        
        # Convert and validate budget_max
        budget_max = self._filter_and_convert_value(budget_max, 'number')
        if budget_max is None:
            return None, []
        
        # Apply strict_max logic - normalize to lowercase for comparison
        strict_max_normalized = str(strict_max).lower() if strict_max is not None else "false"
        if strict_max_normalized == "true":
            # Strict: price <= budget.max
            return "price <= %s", [budget_max]
        else:
            # Flexible: price <= (budget.max * 1.1)
            flexible_max = int(budget_max * 1.1)
            return "price <= %s", [flexible_max]
    
    def validate_json_structure(self, json_structure):
        """
        Validate that the JSON structure is valid for SQL conversion
        
        This MUST be called before convert_to_sql() to ensure the JSON
        matches the Vehicle Selection V1 schema contract precisely.
        
        Args:
            json_structure: Dictionary containing query structure
        
        Returns:
            bool: True if valid
        
        Raises:
            ValueError: If structure is invalid with details
        """
        if not isinstance(json_structure, dict):
            raise ValueError("JSON structure must be a dictionary")
        
        # Validate against Vehicle Selection V1 schema
        is_valid, error_message = self.validator.validate(json_structure)
        if not is_valid:
            raise ValueError(f"JSON structure validation failed: {error_message}")
        
        return True

