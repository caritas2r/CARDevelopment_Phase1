# Feature Enum Analysis Summary

## Current Schema Features (25 total)
All features currently in the JSON schema:
- backup_camera
- blind_spot_monitoring
- adaptive_cruise_control
- apple_carplay
- android_auto
- heated_seats
- leather_seats
- sunroof
- third_row_seating
- lane_keep_assist
- lane_departure_warning
- front_parking_sensors
- rear_parking_sensors
- remote_start
- heated_steering_wheel
- ventilated_seats
- wireless_charging
- premium_audio
- built_in_navigation
- roof_rack
- tow_package
- panoramic_roof
- memory_seats
- keyless_entry
- unspecified

## Features Found in CSV (15 mapped)
These features from the schema were found in the CSV analysis:
- adaptive_cruise_control (97 occurrences)
- android_auto (77 occurrences)
- apple_carplay (118 occurrences)
- backup_camera (80 occurrences)
- blind_spot_monitoring (84 occurrences)
- built_in_navigation (37 occurrences)
- heated_seats (115 occurrences)
- heated_steering_wheel (85 occurrences)
- keyless_entry (42 occurrences)
- lane_keep_assist (38 occurrences)
- leather_seats (99 occurrences)
- remote_start (89 occurrences)
- sunroof (129 occurrences - note: includes "sunroof/panoramic roof" combined entries)
- third_row_seating (42 occurrences)
- ventilated_seats (36 occurrences)

## Features in Schema but NOT Found in CSV
These features exist in the schema but were not detected in the CSV:
- front_parking_sensors
- lane_departure_warning
- memory_seats
- panoramic_roof (Note: CSV has "sunroof/panoramic roof" combined, which maps to sunroof)
- premium_audio
- rear_parking_sensors
- roof_rack
- tow_package
- wireless_charging

**Note:** Some of these may actually be present in the CSV but weren't detected due to:
1. Different wording/phrasing
2. Combined with other features (e.g., "sunroof/panoramic roof")
3. Not explicitly mentioned in the extracted features column

## Potential New Features to Add

### 1. **bluetooth** (1 occurrence found)
- Found in CSV: "tech: Bluetooth"
- Rationale: Bluetooth connectivity is a common feature request, separate from Apple CarPlay/Android Auto
- Recommendation: **ADD** - This is a legitimate feature that users request

### 2. **rear_entertainment_system** (potential)
- Not explicitly found in CSV, but prompts mention:
  - "drop-down movie player" (Honda Odyssey Touring)
  - Entertainment features for minivans
- Rationale: Common in family vehicles, especially minivans
- Recommendation: **CONSIDER** - May be worth adding if family/minivan use cases are important

### 3. **sliding_doors** (potential)
- Not explicitly found in CSV, but prompts mention:
  - "sliding doors" (Honda Odyssey)
- Rationale: Important feature for minivans
- Recommendation: **CONSIDER** - Only relevant for minivans, may be too specific

## Issues Identified

### 1. **Panoramic Roof vs Sunroof**
- **Problem**: CSV has "sunroof/panoramic roof" as a combined feature string
- **Impact**: `panoramic_roof` feature in schema is not being detected even though it exists
- **Recommendation**: Update CSV parsing to handle combined features, or add logic to detect when both should be marked

### 2. **Feature Detection Gaps**
Many features in the schema weren't detected, possibly because:
- They're mentioned in prompts but not extracted to the features column
- Different terminology is used
- They're less commonly requested

## Recommendations

### High Priority
1. **Add `bluetooth`** to the feature_tag enum - it's explicitly mentioned and is a common feature

### Medium Priority
2. **Review panoramic_roof detection** - The CSV combines "sunroof/panoramic roof" which may need special handling
3. **Verify missing features** - Check if features like `premium_audio`, `roof_rack`, `tow_package`, `wireless_charging` are actually in the prompts but not extracted

### Low Priority
4. **Consider `rear_entertainment_system`** - If family/minivan use cases are important
5. **Consider `sliding_doors`** - Only if minivan-specific features are needed

## Notes
- Most "unmapped" features in the CSV are actually not features but other schema fields:
  - Transmission types (already in `powertrain_drivability.transmission`)
  - Body styles (already in `vehicle_type`)
  - Drivetrain (already in `powertrain_drivability.drivetrain`)
  - Powertrain types (already in `powertrain_drivability.powertrain_type`)
  - Price/mileage constraints (already in `ownership_constraints`)
  - Colors (already in `preference_signals.color`)

