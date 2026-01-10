"""
Output Quality Service - Checks quality of model inference output
"""
from typing import Dict, Any, List, Tuple


class OutputQualityService:
    """Service responsible for checking quality of model inference output"""
    
    def __init__(self):
        """Initialize the output quality service"""
        self.name = "output-quality-service"
        self.initialized = False
    
    def register(self, app):
        """Register routes and functionality with the Flask app"""
        pass
    
    def initialize(self):
        """Initialize the service"""
        if not self.initialized:
            print(f"[{self.name}] Initializing...")
            self.initialized = True
            print(f"[{self.name}] Initialized successfully")
    
    def check_output_quality(self, json_output: Dict[str, Any], original_query: str) -> Tuple[bool, List[str]]:
        """
        Check the quality of model inference output
        
        Args:
            json_output: The JSON output from model inference
            original_query: The original natural language query
        
        Returns:
            Tuple of (is_acceptable, warnings)
            - is_acceptable: True if output quality is acceptable, False if there are issues
            - warnings: List of warning messages describing quality issues
        """
        warnings = []
        
        # Check 1: Is the output empty or None?
        if not json_output or not isinstance(json_output, dict):
            warnings.append("Output is empty or not a dictionary")
            return False, warnings
        
        # Check 2: Are all fields unspecified? (no constraints extracted)
        if self._all_fields_unspecified(json_output):
            warnings.append("No constraints extracted - all fields are 'unspecified'")
            return False, warnings
        
        # Check 3: Are critical fields missing?
        critical_fields = ['make', 'model', 'vehicle_type', 'ownership_constraints']
        missing_critical = []
        for field in critical_fields:
            if field not in json_output:
                missing_critical.append(field)
        
        if missing_critical:
            warnings.append(f"Missing critical fields: {', '.join(missing_critical)}")
        
        # Check 4: Are arrays empty when they should have values?
        # (This is more of a semantic check - harder to automate)
        
        # Check 5: Are there contradictory constraints?
        # (e.g., year_min > year_max, budget_min > budget_max)
        contradiction_warnings = self._check_contradictions(json_output)
        warnings.extend(contradiction_warnings)
        
        # Determine if acceptable (warnings are okay, but critical issues are not)
        is_acceptable = len([w for w in warnings if "No constraints extracted" in w or "Output is empty" in w]) == 0
        
        return is_acceptable, warnings
    
    def _all_fields_unspecified(self, json_output: Dict[str, Any]) -> bool:
        """
        Check if all extractable fields are unspecified
        
        Args:
            json_output: The JSON output from model
        
        Returns:
            bool: True if all fields are unspecified
        """
        # Check top-level fields that should have values
        has_specified_make = self._has_specified_value(json_output.get('make', []))
        has_specified_model = self._has_specified_value(json_output.get('model', []))
        
        # Check nested structures
        vehicle_type = json_output.get('vehicle_type', {})
        has_body_styles = (
            self._has_specified_value(vehicle_type.get('include_body_styles', [])) or
            self._has_specified_value(vehicle_type.get('exclude_body_styles', []))
        )
        
        ownership = json_output.get('ownership_constraints', {})
        has_budget = (
            ownership.get('budget', {}).get('min') != 'unspecified' or
            ownership.get('budget', {}).get('max') != 'unspecified'
        )
        has_year = (
            ownership.get('year', {}).get('min') != 'unspecified' or
            ownership.get('year', {}).get('max') != 'unspecified'
        )
        has_mileage = (
            ownership.get('mileage', {}).get('max') != 'unspecified' or
            self._has_specified_value(ownership.get('mileage', {}).get('qualitative', []))
        )
        
        intended_use = json_output.get('intended_use', {})
        has_use_cases = self._has_specified_value(intended_use.get('use_case_tags', []))
        
        powertrain = json_output.get('powertrain_drivability', {})
        has_powertrain = self._has_specified_value(powertrain.get('powertrain_type', []))
        has_transmission = powertrain.get('transmission') != 'unspecified'
        has_drivetrain = powertrain.get('drivetrain') != 'unspecified'
        
        # If none of these have values, then all fields are unspecified
        return not any([
            has_specified_make, has_specified_model, has_body_styles,
            has_budget, has_year, has_mileage, has_use_cases,
            has_powertrain, has_transmission, has_drivetrain
        ])
    
    def _has_specified_value(self, value: Any) -> bool:
        """Check if a value is specified (not unspecified, not empty, not None)"""
        if value is None:
            return False
        if isinstance(value, list):
            return len([v for v in value if v != 'unspecified' and v is not None]) > 0
        if isinstance(value, str):
            return value != 'unspecified' and value.strip() != ''
        return value != 'unspecified'
    
    def _check_contradictions(self, json_output: Dict[str, Any]) -> List[str]:
        """
        Check for contradictory constraints in the output
        
        Args:
            json_output: The JSON output from model
        
        Returns:
            List of warning messages about contradictions
        """
        warnings = []
        
        ownership = json_output.get('ownership_constraints', {})
        
        # Check year range
        year = ownership.get('year', {})
        year_min = year.get('min')
        year_max = year.get('max')
        if (year_min != 'unspecified' and year_max != 'unspecified' and 
            isinstance(year_min, (int, float)) and isinstance(year_max, (int, float)) and
            year_min > year_max):
            warnings.append(f"Contradictory year range: min ({year_min}) > max ({year_max})")
        
        # Check budget range
        budget = ownership.get('budget', {})
        budget_min = budget.get('min')
        budget_max = budget.get('max')
        if (budget_min != 'unspecified' and budget_max != 'unspecified' and
            isinstance(budget_min, (int, float)) and isinstance(budget_max, (int, float)) and
            budget_min > budget_max):
            warnings.append(f"Contradictory budget range: min ({budget_min}) > max ({budget_max})")
        
        return warnings
