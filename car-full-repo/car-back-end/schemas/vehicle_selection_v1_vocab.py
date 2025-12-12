"""
Canonical vocabulary definitions for Vehicle Selection V1
These vocabularies should be used during parsing and training.
"""

# Body styles
BODY_STYLES = [
    "sedan",
    "coupe",
    "hatchback",
    "wagon",
    "suv",
    "crossover",
    "van",
    "truck"
]

# Priority levels
PRIORITY_LEVELS = [
    "low",
    "medium",
    "high",
    None
]

# Use case tags
USE_CASE_TAGS = [
    "family",
    "animals",
    "commute",
    "cargo",
    "travel",
    "work_light"
]

# Transmission types
TRANSMISSIONS = [
    "automatic",
    "manual",
    "other",
    "unspecified"
]

# Drivetrain types
DRIVETRAINS = [
    "AWD",
    "4WD",
    "FWD",
    "RWD",
    "unspecified"
]

# Powertrain types
POWERTRAIN_TYPES = [
    "gas",
    "hybrid",
    "plug_in_hybrid",
    "electric",
    "diesel",
    "unspecified"
]

# Feature tags
FEATURE_TAGS = [
    "backup_camera",
    "blind_spot_monitoring",
    "adaptive_cruise_control",
    "apple_carplay",
    "android_auto",
    "heated_seats",
    "leather_seats",
    "sunroof",
    "third_row_seating"
]

# Mileage qualitative values
MILEAGE_QUALITATIVE = [
    "low",
    "moderate",
    "high",
    "low_or_moderate",
    None
]

# Maintenance priority values
MAINTENANCE_PRIORITIES = [
    "low_cost",
    "balanced",
    "performance_first",
    "unspecified"
]

# Safety priority values
SAFETY_PRIORITIES = [
    "baseline",
    "enhanced",
    "unspecified"
]

