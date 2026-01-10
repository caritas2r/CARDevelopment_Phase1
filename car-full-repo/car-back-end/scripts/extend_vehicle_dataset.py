"""
Script to extend the vehicle dataset CSV with columns from the JSON schema.

This script adds columns for all fields in vehicle_selection_v1_schema.json
to create a comprehensive vehicle database.
"""

import csv
import json
import os

# Paths
SCHEMA_PATH = 'car-back-end/schemas/vehicle_selection_v1_schema.json'
INPUT_CSV = r'C:\Users\Sol\Downloads\sample_nlp_mockaroo_seed_data_combined.csv'
OUTPUT_CSV = r'C:\Users\Sol\Downloads\sample_nlp_mockaroo_seed_data_extended.csv'

def load_schema():
    """Load the JSON schema to understand the structure."""
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_existing_columns(input_file):
    """Get the existing columns from the CSV file."""
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames

def get_schema_fields(schema):
    """
    Extract field names from the schema that need to be columns.
    Returns a list of column names we should add.
    """
    fields = []
    
    # Top-level fields
    properties = schema.get('properties', {})
    
    # trim
    if 'trim' in properties:
        fields.append('trim')
    
    # vehicle_type fields (flattened)
    if 'vehicle_type' in properties:
        fields.append('body_style')  # Main body style (from include_body_styles)
        # exclude_body_styles - REMOVED (query criteria, not inventory data)
    
    # capacity_practicality fields
    if 'capacity_practicality' in properties:
        cap_props = properties['capacity_practicality'].get('properties', {})
        if 'kid_count' in cap_props:
            fields.append('kid_count')
        if 'pet_count' in cap_props:
            fields.append('pet_count')
        # cargo_priority - ADDED BACK for dataset population
        fields.append('cargo_priority')
        # cargo_flexibility fields - ADDED BACK with renamed columns
        fields.append('has_hatch_access')  # Renamed from wants_hatch_access
        fields.append('has_fold_flat_seats')  # Renamed from wants_fold_flat_seats
    
    # intended_use fields
    if 'intended_use' in properties:
        fields.append('use_case_tags')  # Could be comma-separated
    
    # powertrain_drivability fields
    if 'powertrain_drivability' in properties:
        pow_props = properties['powertrain_drivability'].get('properties', {})
        if 'transmission' in pow_props:
            fields.append('transmission')
        if 'drivetrain' in pow_props:
            fields.append('drivetrain')
        if 'powertrain_type' in pow_props:
            fields.append('powertrain_type')  # Could be comma-separated
        if 'fuel_economy_priority' in pow_props:
            fields.append('fuel_economy_priority')
    
    # features_amenities - single 'features' column instead of separate must_have/nice_to_have/avoid
    fields.append('features')  # Comma-separated feature tags
    
    # ownership_constraints fields
    # budget fields - REMOVED (query criteria, not inventory data)
    # mileage qualitative - REMOVED (query criteria, not inventory data)
    
    # preference_signals fields
    if 'preference_signals' in properties:
        pref_props = properties['preference_signals'].get('properties', {})
        if 'reliability_maintenance_priority' in pref_props:
            fields.append('reliability')  # Renamed from reliability_maintenance_priority
        # color - already exists but is empty
    
    # location_constraints fields
    # radius_miles - REMOVED (query criteria, not inventory data)
    
    return fields

def extend_dataset(input_file, output_file):
    """Extend the CSV dataset with new columns from the schema."""
    
    # Load schema
    schema = load_schema()
    
    # Get existing columns
    existing_columns = list(get_existing_columns(input_file))
    print(f"Existing columns: {existing_columns}")
    
    # Get new columns to add
    new_columns = get_schema_fields(schema)
    print(f"\nNew columns to add: {new_columns}")
    
    # Create full column list (maintain order: existing first, then new)
    all_columns = existing_columns + new_columns
    print(f"\nTotal columns: {len(all_columns)}")
    
    # Read input and write output
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=all_columns)
        
        # Write header
        writer.writeheader()
        
        # Process rows
        row_count = 0
        for row in reader:
            # Create new row with all columns
            new_row = {col: row.get(col, '') for col in existing_columns}
            
            # Initialize new columns as empty
            for col in new_columns:
                new_row[col] = ''
            
            writer.writerow(new_row)
            row_count += 1
        
        print(f"\nProcessed {row_count} rows")
        print(f"Output written to: {output_file}")

if __name__ == '__main__':
    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    os.chdir(project_root)
    
    print(f"Working directory: {os.getcwd()}")
    print(f"Input file: {INPUT_CSV}")
    print(f"Output file: {OUTPUT_CSV}\n")
    
    extend_dataset(INPUT_CSV, OUTPUT_CSV)
    
    print("\nDataset extension complete!")
    print("\nNote: New columns are empty and need to be populated with appropriate data.")

