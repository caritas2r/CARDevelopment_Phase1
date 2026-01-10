"""
Script to populate the extended vehicle dataset CSV with random values.

This script populates empty columns with appropriate random values based on
the JSON schema enums and value ranges.
"""

import csv
import random
import os

# Paths
INPUT_CSV = r'C:\Users\Sol\Downloads\sample_nlp_mockaroo_seed_data_extended.csv'
OUTPUT_CSV = r'C:\Users\Sol\Downloads\sample_nlp_mockaroo_seed_data_populated.csv'

# Enum values from vehicle_selection_v1_schema.json
COLOR_ENUMS = [
    'black', 'white', 'silver', 'gray', 'grey', 'red', 'blue', 'green', 'brown',
    'beige', 'tan', 'gold', 'orange', 'yellow', 'purple', 'burgundy', 'maroon',
    'navy', 'teal', 'pink'
]

BODY_STYLE_ENUMS = [
    'sedan', 'coupe', 'hatchback', 'wagon', 'suv', 'crossover', 'van', 'truck',
    'convertible', 'minivan'
]

TRANSMISSION_ENUMS = [
    'automatic', 'manual', 'other', 'cvt', 'dual_clutch'
]

DRIVETRAIN_ENUMS = [
    'AWD', '4WD', 'FWD', 'RWD'
]

POWERTRAIN_TYPE_ENUMS = [
    'gas', 'hybrid', 'plug_in_hybrid', 'electric', 'diesel', 'mild_hybrid'
]

PRIORITY_LEVEL_ENUMS = [
    'low', 'medium', 'high'
]

USE_CASE_TAG_ENUMS = [
    'family', 'animals', 'commute', 'cargo', 'travel', 'work_light', 'pleasure',
    'performance', 'rideshare', 'towing', 'off_road', 'luxury', 'budget_value'
]

FEATURE_TAG_ENUMS = [
    'backup_camera', 'blind_spot_monitoring', 'adaptive_cruise_control',
    'apple_carplay', 'android_auto', 'heated_seats', 'leather_seats',
    'sunroof', 'third_row_seating', 'lane_keep_assist', 'lane_departure_warning',
    'front_parking_sensors', 'rear_parking_sensors', 'remote_start',
    'heated_steering_wheel', 'ventilated_seats', 'wireless_charging',
    'premium_audio', 'built_in_navigation', 'roof_rack', 'tow_package',
    'panoramic_roof', 'panoramic_sunroof', 'memory_seats', 'keyless_entry',
    'bluetooth', 'rear_entertainment_system', 'sliding_doors'
]

CARGO_PRIORITY_ENUMS = [
    'low', 'medium', 'high'
]

RELIABILITY_ENUMS = [
    'low', 'medium', 'high'
]


def populate_row(row):
    """
    Populate a row dictionary with random values for empty columns.
    Modifies the row dictionary in place.
    """
    # Color - random enum value
    if not row.get('color', '').strip():
        row['color'] = random.choice(COLOR_ENUMS)
    
    # Body style - random enum value
    if not row.get('body_style', '').strip():
        row['body_style'] = random.choice(BODY_STYLE_ENUMS)
    
    # Kid count - random 0-7
    if not row.get('kid_count', '').strip():
        row['kid_count'] = str(random.randint(0, 7))
    
    # Pet count - random 0-7
    if not row.get('pet_count', '').strip():
        row['pet_count'] = str(random.randint(0, 7))
    
    # Cargo priority - random enum value
    if not row.get('cargo_priority', '').strip():
        row['cargo_priority'] = random.choice(CARGO_PRIORITY_ENUMS)
    
    # Has hatch access - random T/F boolean
    if not row.get('has_hatch_access', '').strip():
        row['has_hatch_access'] = random.choice(['T', 'F'])
    
    # Has fold flat seats - random T/F boolean
    if not row.get('has_fold_flat_seats', '').strip():
        row['has_fold_flat_seats'] = random.choice(['T', 'F'])
    
    # Features - up to 10 random feature tags (comma-separated)
    if not row.get('features', '').strip():
        num_features = random.randint(0, 10)
        selected_features = random.sample(FEATURE_TAG_ENUMS, min(num_features, len(FEATURE_TAG_ENUMS)))
        row['features'] = ','.join(selected_features) if selected_features else ''
    
    # Use case tags - up to 3 random tags (comma-separated)
    if not row.get('use_case_tags', '').strip():
        num_tags = random.randint(0, 3)
        selected_tags = random.sample(USE_CASE_TAG_ENUMS, min(num_tags, len(USE_CASE_TAG_ENUMS)))
        row['use_case_tags'] = ','.join(selected_tags) if selected_tags else ''
    
    # Transmission - 1 random value
    if not row.get('transmission', '').strip():
        row['transmission'] = random.choice(TRANSMISSION_ENUMS)
    
    # Drivetrain - 1 random value
    if not row.get('drivetrain', '').strip():
        row['drivetrain'] = random.choice(DRIVETRAIN_ENUMS)
    
    # Powertrain type - 1 random value
    if not row.get('powertrain_type', '').strip():
        row['powertrain_type'] = random.choice(POWERTRAIN_TYPE_ENUMS)
    
    # Fuel economy priority - 1 random value
    if not row.get('fuel_economy_priority', '').strip():
        row['fuel_economy_priority'] = random.choice(PRIORITY_LEVEL_ENUMS)
    
    # Reliability - 1 random value
    if not row.get('reliability', '').strip():
        row['reliability'] = random.choice(RELIABILITY_ENUMS)
    
    return row


def populate_dataset(input_file, output_file):
    """Populate the CSV dataset with random values."""
    
    rows_processed = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames)
        
        # Add missing columns if they don't exist
        # Insert has_hatch_access and has_fold_flat_seats after body_style
        if 'has_hatch_access' not in fieldnames:
            body_style_idx = fieldnames.index('body_style') if 'body_style' in fieldnames else len(fieldnames)
            fieldnames.insert(body_style_idx + 1, 'has_hatch_access')
        
        if 'has_fold_flat_seats' not in fieldnames:
            has_hatch_idx = fieldnames.index('has_hatch_access') if 'has_hatch_access' in fieldnames else len(fieldnames)
            fieldnames.insert(has_hatch_idx + 1, 'has_fold_flat_seats')
        
        # Insert cargo_priority after pet_count
        if 'cargo_priority' not in fieldnames:
            pet_count_idx = fieldnames.index('pet_count') if 'pet_count' in fieldnames else len(fieldnames)
            fieldnames.insert(pet_count_idx + 1, 'cargo_priority')
        
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            # Ensure new columns exist in row dict (initialize as empty if missing)
            for col in fieldnames:
                if col not in row:
                    row[col] = ''
            
            # Populate the row
            populated_row = populate_row(row)
            writer.writerow(populated_row)
            rows_processed += 1
            
            if rows_processed % 500 == 0:
                print(f"Processed {rows_processed} rows...")
    
    print(f"\nProcessed {rows_processed} rows total")
    print(f"Output written to: {output_file}")


if __name__ == '__main__':
    print("Vehicle Dataset Population Script")
    print("=" * 50)
    print(f"Input file: {INPUT_CSV}")
    print(f"Output file: {OUTPUT_CSV}\n")
    
    if not os.path.exists(INPUT_CSV):
        print(f"ERROR: Input file not found: {INPUT_CSV}")
        exit(1)
    
    populate_dataset(INPUT_CSV, OUTPUT_CSV)
    
    print("\nDataset population complete!")

