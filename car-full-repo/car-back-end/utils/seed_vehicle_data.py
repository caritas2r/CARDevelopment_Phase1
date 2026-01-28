#!/usr/bin/env python3
"""
Seed vehicle database with expanded data
Generates vehicles from 20 manufacturers with 10 models each
"""
import sqlite3
import random
import os
from pathlib import Path

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'car_database.db')

# 20 Car Manufacturers
MAKES = [
    'Toyota', 'Honda', 'Ford', 'Chevrolet', 'BMW',
    'Mercedes-Benz', 'Audi', 'Volkswagen', 'Nissan', 'Hyundai',
    'Kia', 'Mazda', 'Subaru', 'Jeep', 'Ram',
    'GMC', 'Lexus', 'Acura', 'Infiniti', 'Cadillac'
]

# Generic models per manufacturer (10 models each)
MODELS_PER_MAKE = {
    'Toyota': ['Camry', 'Corolla', 'RAV4', 'Highlander', 'Prius', 'Tacoma', 'Tundra', '4Runner', 'Sienna', 'Avalon'],
    'Honda': ['Accord', 'Civic', 'CR-V', 'Pilot', 'Odyssey', 'Ridgeline', 'Passport', 'HR-V', 'Fit', 'Insight'],
    'Ford': ['F-150', 'Escape', 'Explorer', 'Mustang', 'Edge', 'Expedition', 'Fusion', 'Bronco', 'Ranger', 'Transit'],
    'Chevrolet': ['Silverado', 'Equinox', 'Tahoe', 'Malibu', 'Traverse', 'Suburban', 'Camaro', 'Colorado', 'Trax', 'Blazer'],
    'BMW': ['3 Series', '5 Series', 'X3', 'X5', 'X1', '7 Series', 'X7', '4 Series', '2 Series', 'iX'],
    'Mercedes-Benz': ['C-Class', 'E-Class', 'S-Class', 'GLE', 'GLC', 'GLS', 'A-Class', 'CLA', 'G-Class', 'EQE'],
    'Audi': ['A4', 'A6', 'Q5', 'Q7', 'Q3', 'A3', 'A8', 'e-tron', 'Q8', 'TT'],
    'Volkswagen': ['Jetta', 'Passat', 'Tiguan', 'Atlas', 'Golf', 'Arteon', 'ID.4', 'Touareg', 'Beetle', 'CC'],
    'Nissan': ['Altima', 'Sentra', 'Rogue', 'Pathfinder', 'Frontier', 'Titan', 'Maxima', 'Murano', 'Armada', 'Leaf'],
    'Hyundai': ['Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Palisade', 'Kona', 'Venue', 'Ioniq', 'Genesis', 'Veloster'],
    'Kia': ['Optima', 'Forte', 'Sportage', 'Sorento', 'Telluride', 'Soul', 'Rio', 'Stinger', 'Carnival', 'EV6'],
    'Mazda': ['Mazda3', 'Mazda6', 'CX-5', 'CX-9', 'CX-30', 'MX-5 Miata', 'CX-3', 'Tribute', 'Protege', 'B-Series'],
    'Subaru': ['Outback', 'Forester', 'Crosstrek', 'Ascent', 'Legacy', 'Impreza', 'WRX', 'BRZ', 'Baja', 'Tribeca'],
    'Jeep': ['Wrangler', 'Grand Cherokee', 'Cherokee', 'Compass', 'Renegade', 'Gladiator', 'Commander', 'Patriot', 'Liberty', 'Wagoneer'],
    'Ram': ['1500', '2500', '3500', 'Promaster', 'ProMaster City', 'Dakota', 'Durango', 'Ramcharger', 'C/V Tradesman', 'Rebel'],
    'GMC': ['Sierra', 'Yukon', 'Acadia', 'Terrain', 'Canyon', 'Envoy', 'Savana', 'Sierra Denali', 'Yukon XL', 'Jimmy'],
    'Lexus': ['ES', 'RX', 'NX', 'GX', 'LX', 'IS', 'LC', 'LS', 'UX', 'RC'],
    'Acura': ['MDX', 'RDX', 'TLX', 'ILX', 'RLX', 'NSX', 'Integra', 'CL', 'TL', 'RL'],
    'Infiniti': ['Q50', 'Q60', 'QX50', 'QX60', 'QX80', 'QX30', 'Q70', 'QX70', 'FX', 'G'],
    'Cadillac': ['Escalade', 'XT5', 'XT4', 'XT6', 'CT5', 'CT4', 'XTS', 'ATS', 'SRX', 'CTS']
}

# Enum values from schema
BODY_STYLES = ['sedan', 'coupe', 'hatchback', 'wagon', 'suv', 'crossover', 'van', 'truck', 'convertible', 'minivan']
TRANSMISSIONS = ['automatic', 'manual', 'other', 'cvt', 'dual_clutch']
DRIVETRAINS = ['AWD', '4WD', 'FWD', 'RWD']
COLORS = ['black', 'white', 'silver', 'gray', 'grey', 'red', 'blue', 'green', 'brown',
          'beige', 'tan', 'gold', 'orange', 'yellow', 'purple', 'burgundy', 'maroon',
          'navy', 'teal', 'pink']
CARGO_SPACES = ['none', 'low', 'medium', 'high', 'unknown']
FUEL_ECONOMIES = ['low', 'medium', 'high', 'unknown']
RELIABILITIES = ['low', 'medium', 'high', 'unknown']

FEATURES = [
    'backup_camera', 'blind_spot_monitoring', 'adaptive_cruise_control',
    'apple_carplay', 'android_auto', 'heated_seats', 'leather_seats',
    'sunroof', 'third_row_seating', 'lane_keep_assist', 'lane_departure_warning',
    'front_parking_sensors', 'rear_parking_sensors', 'remote_start',
    'heated_steering_wheel', 'ventilated_seats', 'wireless_charging',
    'premium_audio', 'built_in_navigation', 'roof_rack', 'tow_package',
    'panoramic_roof', 'panoramic_sunroof', 'memory_seats', 'keyless_entry',
    'bluetooth', 'rear_entertainment_system', 'sliding_doors'
]

USE_CASE_TAGS = [
    'family', 'animals', 'commute', 'cargo', 'travel', 'work_light',
    'pleasure', 'performance', 'rideshare', 'towing', 'off_road', 'luxury', 'budget_value'
]

POWERTRAIN_TYPES = ['gas', 'hybrid', 'plug_in_hybrid', 'electric', 'diesel', 'mild_hybrid']

# Sample cities and states
CITIES = [
    ('New York', 'NY'), ('Los Angeles', 'CA'), ('Chicago', 'IL'), ('Houston', 'TX'),
    ('Phoenix', 'AZ'), ('Philadelphia', 'PA'), ('San Antonio', 'TX'), ('San Diego', 'CA'),
    ('Dallas', 'TX'), ('San Jose', 'CA'), ('Austin', 'TX'), ('Jacksonville', 'FL'),
    ('Fort Worth', 'TX'), ('Columbus', 'OH'), ('Charlotte', 'NC'), ('San Francisco', 'CA'),
    ('Indianapolis', 'IN'), ('Seattle', 'WA'), ('Denver', 'CO'), ('Boston', 'MA')
]

TRIMS = ['Base', 'LE', 'LX', 'SE', 'XLE', 'EX', 'Limited', 'Premium', 'Sport', 'Touring', 
         'LT', 'LS', 'LTZ', 'SR', 'SR5', 'SL', 'SV', 'SLT', 'Denali', 'Platinum']


def generate_zip_code():
    """Generate a random 5-digit zip code"""
    return str(random.randint(10000, 99999))


def generate_vehicle_id(vehicle_counter):
    """Generate a unique vehicle ID"""
    return f'vehicle_{vehicle_counter}'


def seed_vehicles(conn, vehicles_per_make_model=4):
    """
    Seed vehicle data
    
    Args:
        conn: Database connection
        vehicles_per_make_model: Number of vehicles to generate per make/model combination
    """
    cursor = conn.cursor()
    
    # Get current vehicle count to start numbering
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    existing_count = cursor.fetchone()[0]
    vehicle_counter = existing_count + 1
    
    print(f"Existing vehicles in database: {existing_count}")
    print(f"Starting vehicle ID counter at: {vehicle_counter}")
    print(f"Generating vehicles from {len(MAKES)} manufacturers...")
    print()
    
    total_vehicles = 0
    
    for make in MAKES:
        models = MODELS_PER_MAKE[make]
        print(f"Processing {make}...")
        
        for model in models:
            # Generate 4-5 vehicles per make/model (randomized)
            num_vehicles = random.randint(vehicles_per_make_model, vehicles_per_make_model + 1)
            
            for _ in range(num_vehicles):
                vehicle_id = generate_vehicle_id(vehicle_counter)
                vehicle_counter += 1
                total_vehicles += 1
                
                # Required fields
                year = random.randint(1970, 2026)
                price = random.randint(5000, 100000)
                mileage = random.randint(0, 200000)
                currency = 840  # USD
                
                # Optional fields (randomized)
                trim = random.choice(TRIMS) if random.random() < 0.7 else None
                body_style = random.choice(BODY_STYLES) if random.random() < 0.9 else None
                transmission = random.choice(TRANSMISSIONS) if random.random() < 0.9 else None
                drivetrain = random.choice(DRIVETRAINS) if random.random() < 0.9 else None
                seating_capacity = random.randint(2, 8) if random.random() < 0.8 else None
                color = random.choice(COLORS) if random.random() < 0.9 else None
                cargo_space = random.choice(CARGO_SPACES) if random.random() < 0.7 else None
                has_hatch_access = random.choice([0, 1]) if random.random() < 0.5 else None
                has_fold_flat_seats = random.choice([0, 1]) if random.random() < 0.5 else None
                fuel_economy = random.choice(FUEL_ECONOMIES) if random.random() < 0.8 else None
                reliability = random.choice(RELIABILITIES) if random.random() < 0.8 else None
                
                # Location
                city, state = random.choice(CITIES) if random.random() < 0.8 else (None, None)
                zip_code = generate_zip_code() if city else None
                number_of_owners = random.randint(1, 4) if random.random() < 0.7 else None
                
                # Insert vehicle
                cursor.execute("""
                    INSERT INTO vehicles (
                        vehicle_id, make, model, trim, year, price, currency, mileage,
                        body_style, transmission, drivetrain, seating_capacity, color,
                        cargo_space, has_hatch_access, has_fold_flat_seats,
                        fuel_economy, reliability, city, state_region, zip_code, number_of_owners
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vehicle_id, make, model, trim, year, price, currency, mileage,
                    body_style, transmission, drivetrain, seating_capacity, color,
                    cargo_space, has_hatch_access, has_fold_flat_seats,
                    fuel_economy, reliability, city, state, zip_code, number_of_owners
                ))
                
                # Features (2-5 random features)
                num_features = random.randint(2, 5)
                selected_features = random.sample(FEATURES, min(num_features, len(FEATURES)))
                for feature in selected_features:
                    cursor.execute("""
                        INSERT INTO vehicle_features (vehicle_id, feature_tag)
                        VALUES (?, ?)
                    """, (vehicle_id, feature))
                
                # Use case tags (1-4 random tags)
                num_tags = random.randint(1, 4)
                selected_tags = random.sample(USE_CASE_TAGS, min(num_tags, len(USE_CASE_TAGS)))
                for tag in selected_tags:
                    cursor.execute("""
                        INSERT INTO vehicle_use_case_tags (vehicle_id, use_case_tag)
                        VALUES (?, ?)
                    """, (vehicle_id, tag))
                
                # Powertrain types (1-2 types, but only one for most)
                if random.random() < 0.85:
                    # Single powertrain type
                    powertrain = random.choice(POWERTRAIN_TYPES)
                    cursor.execute("""
                        INSERT INTO vehicle_powertrain_types (vehicle_id, powertrain_type)
                        VALUES (?, ?)
                    """, (vehicle_id, powertrain))
                else:
                    # Multiple powertrain types (e.g., plug-in hybrid = hybrid + plug_in_hybrid)
                    if random.random() < 0.5:
                        # Hybrid case
                        cursor.execute("""
                            INSERT INTO vehicle_powertrain_types (vehicle_id, powertrain_type)
                            VALUES (?, ?)
                        """, (vehicle_id, 'hybrid'))
                        cursor.execute("""
                            INSERT INTO vehicle_powertrain_types (vehicle_id, powertrain_type)
                            VALUES (?, ?)
                        """, (vehicle_id, 'plug_in_hybrid'))
                    else:
                        # Just pick two random ones
                        powertrains = random.sample(POWERTRAIN_TYPES, 2)
                        for pt in powertrains:
                            cursor.execute("""
                                INSERT INTO vehicle_powertrain_types (vehicle_id, powertrain_type)
                                VALUES (?, ?)
                            """, (vehicle_id, pt))
    
    conn.commit()
    print()
    print(f"Successfully seeded {total_vehicles} vehicles")
    print(f"  - {len(MAKES)} manufacturers")
    print(f"  - {len(MAKES) * len(MODELS_PER_MAKE[MAKES[0]])} unique make/model combinations")
    print(f"  - Average {vehicles_per_make_model}-{vehicles_per_make_model+1} vehicles per make/model")


def main():
    """Main entry point"""
    # Ensure database directory exists
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Seed vehicles
        seed_vehicles(conn, vehicles_per_make_model=4)
        
        # Verify
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vehicles")
        total = cursor.fetchone()[0]
        print()
        print(f"Total vehicles in database: {total}")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    main()
