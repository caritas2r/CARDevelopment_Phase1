"""
Key Mapping Service - Converts between shortened keys and full keys

This service handles the bidirectional conversion between:
- Shortened keys (mk, md, vt, etc.) - used in training/inference
- Full keys (make, model, vehicle_type, etc.) - used in SQL conversion and schema validation
"""

from typing import Any, Dict


# Reverse mapping: shortened keys -> full keys
SHORT_TO_FULL_MAPPING = {
    # Top-level keys
    "mk": "make",
    "md": "model",
    "tr": "trim",
    "vt": "vehicle_type",
    "cp": "capacity_practicality",
    "iu": "intended_use",
    "pd": "powertrain_drivability",
    "fa": "features_amenities",
    "oc": "ownership_constraints",
    "ps": "preference_signals",
    "lc": "location_constraints",
    # Nested keys - vehicle_type
    "inc": "include_body_styles",
    "exc": "exclude_body_styles",
    # Nested keys - capacity_practicality
    "seat_min": "min_seating_capacity",
    "kids": "kid_count",
    "pets": "pet_count",
    "cargo_pri": "cargo_priority",
    "cargo_fx": "cargo_flexibility",
    # Nested keys - cargo_flexibility
    "hatch": "wants_hatch_access",
    "foldflat": "wants_fold_flat_seats",
    # Nested keys - intended_use
    "tags": "use_case_tags",
    # Nested keys - powertrain_drivability
    "tx": "transmission",
    "dt": "drivetrain",
    "pt": "powertrain_type",
    "fe_pri": "fuel_economy_priority",
    # Nested keys - features_amenities
    "must": "must_have",
    "nice": "nice_to_have",
    # "avoid" stays the same
    # Nested keys - ownership_constraints
    "bud": "budget",
    "yr": "year",
    "mi": "mileage",
    "owners": "number_of_owners",
    # Nested keys - budget
    "cur": "currency",
    "max_strict": "strict_max",
    # "min" and "max" stay the same
    # Nested keys - mileage
    "qual": "qualitative",
    # Nested keys - preference_signals
    "rel_pri": "reliability_maintenance_priority",
    "clr": "color",
    # Nested keys - location_constraints
    "cty": "city",
    "st": "state_region",
    "rad": "radius_miles",
}


def expand_keys(obj: Any) -> Any:
    """
    Recursively convert shortened keys to full keys in a JSON object.
    
    This is the reverse of the key mapping used in training data.
    Converts model output (shortened keys) to full keys for SQL conversion.
    
    Args:
        obj: JSON object with shortened keys (or any nested structure)
    
    Returns:
        JSON object with full keys
    """
    if isinstance(obj, dict):
        expanded = {}
        for key, value in obj.items():
            # Map the key if it exists in SHORT_TO_FULL_MAPPING, otherwise keep original
            new_key = SHORT_TO_FULL_MAPPING.get(key, key)
            # Recursively expand the value
            expanded[new_key] = expand_keys(value)
        return expanded
    elif isinstance(obj, list):
        # Expand each element in the list
        return [expand_keys(item) for item in obj]
    else:
        # Primitives (str, int, float, bool, None) - return as-is
        return obj


class KeyMappingService:
    """Service for converting between shortened and full key formats"""
    
    def __init__(self):
        """Initialize the key mapping service"""
        self.name = "key-mapping-service"
        self.initialized = False
    
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
            self.initialized = True
            print(f"[{self.name}] Initialized successfully")
    
    def expand_shortened_keys(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert JSON with shortened keys to full keys.
        
        This is used to convert model inference output (which uses shortened keys
        like mk, md, vt) to the full key format expected by SQL conversion and
        schema validation (make, model, vehicle_type).
        
        Args:
            json_data: Dictionary with shortened keys (e.g., from model inference)
        
        Returns:
            Dictionary with full keys (e.g., for SQL conversion)
        
        Example:
            Input:  {"mk": ["Toyota"], "oc": {"bud": {"max": 30000}}}
            Output: {"make": ["Toyota"], "ownership_constraints": {"budget": {"max": 30000}}}
        """
        return expand_keys(json_data)

