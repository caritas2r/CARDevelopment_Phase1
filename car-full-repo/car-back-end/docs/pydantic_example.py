"""
Pydantic Example - Demonstrating schema validation for Vehicle Selection V1

This file shows how to use Pydantic to validate JSON data before converting to SQL.
Pydantic provides type-safe models, automatic validation, and clear error messages.
"""

from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import List, Optional, Union, Literal
from enum import Enum


# ============================================================================
# ENUMS - Define allowed values (from your schema definitions)
# ============================================================================

class BodyStyle(str, Enum):
    SEDAN = "sedan"
    COUPE = "coupe"
    HATCHBACK = "hatchback"
    WAGON = "wagon"
    SUV = "suv"
    CROSSOVER = "crossover"
    VAN = "van"
    TRUCK = "truck"
    CONVERTIBLE = "convertible"
    MINIVAN = "minivan"
    UNSPECIFIED = "unspecified"


class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNSPECIFIED = "unspecified"


class Transmission(str, Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    OTHER = "other"
    CVT = "cvt"
    DUAL_CLUTCH = "dual_clutch"
    UNSPECIFIED = "unspecified"


class Drivetrain(str, Enum):
    AWD = "AWD"
    FOUR_WD = "4WD"
    FWD = "FWD"
    RWD = "RWD"
    UNSPECIFIED = "unspecified"


# ============================================================================
# HELPER TYPES - For fields that can be int OR "unspecified"
# ============================================================================

# Pydantic allows Union types for fields that can be multiple types
# For fields like min_seating_capacity that can be int or "unspecified"
UnspecifiedInt = Union[int, Literal["unspecified"]]
UnspecifiedFloat = Union[float, Literal["unspecified"]]


# ============================================================================
# NESTED MODELS - Represent nested JSON objects
# ============================================================================

class VehicleType(BaseModel):
    """Body style preferences"""
    include_body_styles: List[BodyStyle]
    exclude_body_styles: List[BodyStyle]


class CargoFlexibility(BaseModel):
    """Cargo flexibility preferences"""
    wants_hatch_access: Literal["true", "false", "unspecified"]
    wants_fold_flat_seats: Literal["true", "false", "unspecified"]


class CapacityPracticality(BaseModel):
    """Seating and cargo capacity requirements"""
    min_seating_capacity: UnspecifiedInt = Field(ge=1)  # ge = greater than or equal
    kid_count: UnspecifiedInt = Field(ge=0)
    pet_count: UnspecifiedInt = Field(ge=0)
    cargo_priority: PriorityLevel
    cargo_flexibility: CargoFlexibility


class IntendedUse(BaseModel):
    """Use case tags"""
    use_case_tags: List[str]  # Could use enum if you want stricter validation


class PowertrainDrivability(BaseModel):
    """Powertrain and drivetrain preferences"""
    transmission: Transmission
    drivetrain: Drivetrain
    powertrain_type: List[str]
    fuel_economy_priority: PriorityLevel


class FeaturesAmenities(BaseModel):
    """Feature requirements"""
    must_have: List[str]
    nice_to_have: List[str]
    avoid: List[str]


class Budget(BaseModel):
    """Budget constraints"""
    currency: UnspecifiedInt
    min: UnspecifiedFloat
    max: UnspecifiedFloat
    strict_max: Literal["true", "false", "unspecified"]


class YearConstraints(BaseModel):
    """Year constraints"""
    min: UnspecifiedInt
    max: UnspecifiedInt


class MileageConstraints(BaseModel):
    """Mileage constraints"""
    max: UnspecifiedInt
    qualitative: List[str]


class OwnershipConstraints(BaseModel):
    """Ownership and budget constraints"""
    budget: Budget
    year: YearConstraints
    mileage: MileageConstraints
    number_of_owners: UnspecifiedInt


class PreferenceSignals(BaseModel):
    """User preferences"""
    reliability_maintenance_priority: str
    color: List[str]


class LocationConstraints(BaseModel):
    """Geographic constraints (optional)"""
    city: Optional[str] = None
    state_region: Optional[str] = None
    radius_miles: UnspecifiedFloat


# ============================================================================
# MAIN MODEL - Top-level schema
# ============================================================================

class VehicleSelectionV1(BaseModel):
    """
    Vehicle Selection V1 Schema - Validated model for NLP-to-JSON outputs
    
    This model enforces:
    - Required fields (query_text, vehicle_type, etc.)
    - Type checking (strings, integers, lists, etc.)
    - Enum validation (body styles, priorities, etc.)
    - Nested structure validation
    """
    
    # Required fields
    query_text: str
    vehicle_type: VehicleType
    capacity_practicality: CapacityPracticality
    intended_use: IntendedUse
    powertrain_drivability: PowertrainDrivability
    features_amenities: FeaturesAmenities
    ownership_constraints: OwnershipConstraints
    preference_signals: PreferenceSignals
    
    # Optional fields
    make: Optional[List[str]] = None
    model: Optional[List[str]] = None
    trim: Optional[str] = None
    location_constraints: Optional[LocationConstraints] = None
    
    # Custom validation example: ensure query_text is not empty
    @field_validator('query_text')
    @classmethod
    def validate_query_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('query_text cannot be empty')
        return v.strip()


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_validation():
    """Example: Validating valid JSON data"""
    
    # Valid JSON data (from your model output)
    valid_json = {
        "query_text": "I need an SUV for my family of 5, under $30k, with AWD",
        "make": ["unspecified"],
        "model": ["unspecified"],
        "trim": "unspecified",
        "vehicle_type": {
            "include_body_styles": ["suv"],
            "exclude_body_styles": ["unspecified"]
        },
        "capacity_practicality": {
            "min_seating_capacity": 5,
            "kid_count": "unspecified",
            "pet_count": "unspecified",
            "cargo_priority": "unspecified",
            "cargo_flexibility": {
                "wants_hatch_access": "unspecified",
                "wants_fold_flat_seats": "unspecified"
            }
        },
        "intended_use": {
            "use_case_tags": ["family"]
        },
        "powertrain_drivability": {
            "transmission": "unspecified",
            "drivetrain": "AWD",
            "powertrain_type": ["unspecified"],
            "fuel_economy_priority": "unspecified"
        },
        "features_amenities": {
            "must_have": ["unspecified"],
            "nice_to_have": ["unspecified"],
            "avoid": ["unspecified"]
        },
        "ownership_constraints": {
            "budget": {
                "currency": 840,
                "min": "unspecified",
                "max": 30000,
                "strict_max": "unspecified"
            },
            "year": {
                "min": "unspecified",
                "max": "unspecified"
            },
            "mileage": {
                "max": "unspecified",
                "qualitative": ["unspecified"]
            },
            "number_of_owners": "unspecified"
        },
        "preference_signals": {
            "reliability_maintenance_priority": "unspecified",
            "color": ["unspecified"]
        }
    }
    
    try:
        # Validate and parse JSON into Pydantic model
        validated_data = VehicleSelectionV1(**valid_json)
        print("✓ Validation successful!")
        print(f"  Query: {validated_data.query_text}")
        print(f"  Body Styles: {validated_data.vehicle_type.include_body_styles}")
        print(f"  Drivetrain: {validated_data.powertrain_drivability.drivetrain}")
        print(f"  Max Budget: ${validated_data.ownership_constraints.budget.max}")
        
        # Access data with type safety
        # IDE will provide autocomplete and type checking!
        seating = validated_data.capacity_practicality.min_seating_capacity
        if seating != "unspecified":
            print(f"  Seating: {seating} (type: {type(seating).__name__})")
        
        # Convert back to dict for SQL processing
        data_dict = validated_data.model_dump()
        return validated_data
        
    except ValidationError as e:
        print("✗ Validation failed!")
        print(e.json(indent=2))
        return None


def example_invalid_data():
    """Example: Handling invalid data"""
    
    invalid_json = {
        "query_text": "",  # Empty - will fail custom validator
        "vehicle_type": {
            "include_body_styles": ["invalid_style"],  # Not in enum
            "exclude_body_styles": []
        },
        # Missing required fields...
    }
    
    try:
        validated_data = VehicleSelectionV1(**invalid_json)
    except ValidationError as e:
        print("✗ Validation errors detected:")
        for error in e.errors():
            field_path = " -> ".join(str(x) for x in error["loc"])
            print(f"  {field_path}: {error['msg']}")


def example_sql_conversion(validated_model: VehicleSelectionV1):
    """
    Example: Using validated Pydantic model for SQL conversion
    
    Since the data is validated, you can safely access fields without
    checking for None or invalid types.
    """
    
    conditions = []
    
    # Body style - validated as List[BodyStyle]
    if validated_model.vehicle_type.include_body_styles:
        body_styles = [
            bs.value for bs in validated_model.vehicle_type.include_body_styles 
            if bs != BodyStyle.UNSPECIFIED
        ]
        if body_styles:
            conditions.append(f"body_style IN ({', '.join(repr(bs) for bs in body_styles)})")
    
    # Budget - validated types, can safely check
    budget = validated_model.ownership_constraints.budget
    if budget.max != "unspecified":
        conditions.append(f"price <= {budget.max}")
    
    # Seating capacity - type is Union[int, Literal["unspecified"]]
    seating = validated_model.capacity_practicality.min_seating_capacity
    if isinstance(seating, int):
        conditions.append(f"seating_capacity >= {seating}")
    
    # Drivetrain - validated enum
    drivetrain = validated_model.powertrain_drivability.drivetrain
    if drivetrain != Drivetrain.UNSPECIFIED:
        conditions.append(f"drivetrain = '{drivetrain.value}'")
    
    sql = f"SELECT * FROM vehicles WHERE {' AND '.join(conditions)}"
    return sql


if __name__ == "__main__":
    print("=" * 60)
    print("Pydantic Validation Example")
    print("=" * 60)
    
    print("\n1. Validating valid data:")
    print("-" * 60)
    validated = example_validation()
    
    print("\n2. Handling invalid data:")
    print("-" * 60)
    example_invalid_data()
    
    if validated:
        print("\n3. SQL conversion from validated model:")
        print("-" * 60)
        sql = example_sql_conversion(validated)
        print(f"Generated SQL:\n{sql}")
