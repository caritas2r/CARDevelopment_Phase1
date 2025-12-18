"""
Mock NLP Trip Service - PoC service that returns a sample vehicle from the database
For the proof of concept, this service creates a sample vehicle and returns it
"""
import sqlite3
import random
from typing import Dict, Optional, List


class MockNlpTripService:
    """Mock service for PoC that returns a sample vehicle from the database"""
    
    def __init__(self, database_query_service):
        """
        Initialize the mock NLP trip service
        
        Args:
            database_query_service: DatabaseQueryService instance
        """
        self.name = "mock-nlp-trip-service"
        self.initialized = False
        self.database_query_service = database_query_service
        self.sample_vehicle_id = "poc_sample_vehicle_001"
    
    def register(self, app):
        """Register routes and functionality with the Flask app"""
        # No routes needed - this service is used by QueryService
        pass
    
    def initialize(self):
        """Initialize the service and ensure sample vehicle exists"""
        if not self.initialized:
            print(f"[{self.name}] Initializing...")
            self._ensure_sample_vehicle()
            self.initialized = True
            print(f"[{self.name}] Initialized successfully")
    
    def _ensure_sample_vehicle(self):
        """Ensure a sample vehicle exists in the database, create if missing"""
        conn = self.database_query_service.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if sample vehicle already exists
            cursor.execute("SELECT vehicle_id FROM vehicles WHERE vehicle_id = ?", (self.sample_vehicle_id,))
            if cursor.fetchone():
                print(f"[{self.name}] Sample vehicle already exists: {self.sample_vehicle_id}")
                return
            
            # Create sample vehicle with random valid values
            vehicle_data = self._generate_random_vehicle_data()
            
            # Insert vehicle
            cursor.execute("""
                INSERT INTO vehicles (
                    vehicle_id, make, model, trim, year, price, currency, mileage,
                    body_style, transmission, drivetrain, powertrain_type,
                    seating_capacity, color, cargo_space, has_hatch_access,
                    has_fold_flat_seats, fuel_economy, reliability,
                    city, state_region, zip_code, number_of_owners
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vehicle_data['vehicle_id'],
                vehicle_data['make'],
                vehicle_data['model'],
                vehicle_data['trim'],
                vehicle_data['year'],
                vehicle_data['price'],
                vehicle_data['currency'],
                vehicle_data['mileage'],
                vehicle_data['body_style'],
                vehicle_data['transmission'],
                vehicle_data['drivetrain'],
                vehicle_data['powertrain_type'],
                vehicle_data['seating_capacity'],
                vehicle_data['color'],
                vehicle_data['cargo_space'],
                vehicle_data['has_hatch_access'],
                vehicle_data['has_fold_flat_seats'],
                vehicle_data['fuel_economy'],
                vehicle_data['reliability'],
                vehicle_data['city'],
                vehicle_data['state_region'],
                vehicle_data['zip_code'],
                vehicle_data['number_of_owners']
            ))
            
            # Insert features (random selection)
            if vehicle_data['features']:
                feature_values = [(self.sample_vehicle_id, feature) for feature in vehicle_data['features']]
                cursor.executemany(
                    "INSERT INTO vehicle_features (vehicle_id, feature_tag) VALUES (?, ?)",
                    feature_values
                )
            
            # Insert use case tags (random selection)
            if vehicle_data['use_case_tags']:
                tag_values = [(self.sample_vehicle_id, tag) for tag in vehicle_data['use_case_tags']]
                cursor.executemany(
                    "INSERT INTO vehicle_use_case_tags (vehicle_id, use_case_tag) VALUES (?, ?)",
                    tag_values
                )
            
            conn.commit()
            print(f"[{self.name}] Created sample vehicle: {self.sample_vehicle_id}")
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"[{self.name}] ERROR: Failed to create sample vehicle: {e}")
            raise
    
    def _generate_random_vehicle_data(self) -> Dict:
        """Generate random vehicle data within enum limits"""
        # Enum values from database schema
        body_styles = ['sedan', 'coupe', 'hatchback', 'wagon', 'suv', 'crossover', 'van', 'truck']
        transmissions = ['automatic', 'manual', 'other']
        drivetrains = ['AWD', '4WD', 'FWD', 'RWD']
        powertrain_types = ['gas', 'hybrid', 'plug_in_hybrid', 'electric', 'diesel']
        colors = ['black', 'white', 'silver', 'gray', 'grey', 'red', 'blue', 'green', 'brown',
                  'beige', 'tan', 'gold', 'orange', 'yellow', 'purple', 'burgundy', 'maroon',
                  'navy', 'teal', 'pink']
        cargo_spaces = ['none', 'low', 'medium', 'high', 'unknown']
        fuel_economies = ['low', 'medium', 'high', 'unknown']
        reliabilities = ['low', 'medium', 'high', 'unknown']
        features = ['backup_camera', 'blind_spot_monitoring', 'adaptive_cruise_control',
                   'apple_carplay', 'android_auto', 'heated_seats', 'leather_seats',
                   'sunroof', 'third_row_seating']
        use_case_tags = ['family', 'animals', 'commute', 'cargo', 'travel', 'work_light',
                        'pleasure', 'performance']
        
        # Random makes and models
        makes_models = [
            ('Toyota', 'Camry', 'XLE'),
            ('Honda', 'Accord', 'EX-L'),
            ('Ford', 'F-150', 'Lariat'),
            ('Chevrolet', 'Silverado', 'LTZ'),
            ('BMW', '3 Series', '330i'),
            ('Mercedes-Benz', 'C-Class', 'C300'),
            ('Tesla', 'Model 3', 'Long Range'),
            ('Audi', 'A4', 'Premium'),
            ('Subaru', 'Outback', 'Limited'),
            ('Jeep', 'Grand Cherokee', 'Overland')
        ]
        
        make, model, trim = random.choice(makes_models)
        
        return {
            'vehicle_id': self.sample_vehicle_id,
            'make': make,
            'model': model,
            'trim': trim,
            'year': random.randint(2018, 2024),
            'price': random.randint(20000, 60000),
            'currency': 840,  # USD
            'mileage': random.randint(5000, 80000),
            'body_style': random.choice(body_styles),
            'transmission': random.choice(transmissions),
            'drivetrain': random.choice(drivetrains),
            'powertrain_type': random.choice(powertrain_types),
            'seating_capacity': random.choice([2, 4, 5, 7, 8]),
            'color': random.choice(colors),
            'cargo_space': random.choice(cargo_spaces),
            'has_hatch_access': random.choice([0, 1, None]),
            'has_fold_flat_seats': random.choice([0, 1, None]),
            'fuel_economy': random.choice(fuel_economies),
            'reliability': random.choice(reliabilities),
            'city': random.choice(['Los Angeles', 'New York', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', None]),
            'state_region': random.choice(['CA', 'NY', 'TX', 'FL', 'IL', 'PA', None]),
            'zip_code': random.choice(['90210', '10001', '77001', '33101', '85001', '19101', None]),
            'number_of_owners': random.choice([0, 1, 2, 3, 4, 5, None]),
            'features': random.sample(features, random.randint(1, 4)),
            'use_case_tags': random.sample(use_case_tags, random.randint(1, 3))
        }
    
    def get_sample_vehicle(self) -> Optional[Dict]:
        """
        Generate a new random sample vehicle and return it
        Updates the existing vehicle in the database with new random data each time
        
        Returns:
            Dict containing vehicle data with features and use_case_tags, or None if error
        """
        conn = self.database_query_service.get_connection()
        cursor = conn.cursor()
        
        try:
            # Generate new random vehicle data
            vehicle_data = self._generate_random_vehicle_data()
            
            # Check if vehicle exists, if not create it
            cursor.execute("SELECT vehicle_id FROM vehicles WHERE vehicle_id = ?", (self.sample_vehicle_id,))
            vehicle_exists = cursor.fetchone() is not None
            
            if vehicle_exists:
                # Update existing vehicle
                cursor.execute("""
                    UPDATE vehicles SET
                        make = ?, model = ?, trim = ?, year = ?, price = ?, currency = ?, mileage = ?,
                        body_style = ?, transmission = ?, drivetrain = ?, powertrain_type = ?,
                        seating_capacity = ?, color = ?, cargo_space = ?, has_hatch_access = ?,
                        has_fold_flat_seats = ?, fuel_economy = ?, reliability = ?,
                        city = ?, state_region = ?, zip_code = ?, number_of_owners = ?
                    WHERE vehicle_id = ?
                """, (
                    vehicle_data['make'],
                    vehicle_data['model'],
                    vehicle_data['trim'],
                    vehicle_data['year'],
                    vehicle_data['price'],
                    vehicle_data['currency'],
                    vehicle_data['mileage'],
                    vehicle_data['body_style'],
                    vehicle_data['transmission'],
                    vehicle_data['drivetrain'],
                    vehicle_data['powertrain_type'],
                    vehicle_data['seating_capacity'],
                    vehicle_data['color'],
                    vehicle_data['cargo_space'],
                    vehicle_data['has_hatch_access'],
                    vehicle_data['has_fold_flat_seats'],
                    vehicle_data['fuel_economy'],
                    vehicle_data['reliability'],
                    vehicle_data['city'],
                    vehicle_data['state_region'],
                    vehicle_data['zip_code'],
                    vehicle_data['number_of_owners'],
                    self.sample_vehicle_id
                ))
            else:
                # Insert new vehicle
                cursor.execute("""
                    INSERT INTO vehicles (
                        vehicle_id, make, model, trim, year, price, currency, mileage,
                        body_style, transmission, drivetrain, powertrain_type,
                        seating_capacity, color, cargo_space, has_hatch_access,
                        has_fold_flat_seats, fuel_economy, reliability,
                        city, state_region, zip_code, number_of_owners
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vehicle_data['vehicle_id'],
                    vehicle_data['make'],
                    vehicle_data['model'],
                    vehicle_data['trim'],
                    vehicle_data['year'],
                    vehicle_data['price'],
                    vehicle_data['currency'],
                    vehicle_data['mileage'],
                    vehicle_data['body_style'],
                    vehicle_data['transmission'],
                    vehicle_data['drivetrain'],
                    vehicle_data['powertrain_type'],
                    vehicle_data['seating_capacity'],
                    vehicle_data['color'],
                    vehicle_data['cargo_space'],
                    vehicle_data['has_hatch_access'],
                    vehicle_data['has_fold_flat_seats'],
                    vehicle_data['fuel_economy'],
                    vehicle_data['reliability'],
                    vehicle_data['city'],
                    vehicle_data['state_region'],
                    vehicle_data['zip_code'],
                    vehicle_data['number_of_owners']
                ))
            
            # Delete existing features and tags
            cursor.execute("DELETE FROM vehicle_features WHERE vehicle_id = ?", (self.sample_vehicle_id,))
            cursor.execute("DELETE FROM vehicle_use_case_tags WHERE vehicle_id = ?", (self.sample_vehicle_id,))
            
            # Insert new features
            if vehicle_data['features']:
                feature_values = [(self.sample_vehicle_id, feature) for feature in vehicle_data['features']]
                cursor.executemany(
                    "INSERT INTO vehicle_features (vehicle_id, feature_tag) VALUES (?, ?)",
                    feature_values
                )
            
            # Insert new use case tags
            if vehicle_data['use_case_tags']:
                tag_values = [(self.sample_vehicle_id, tag) for tag in vehicle_data['use_case_tags']]
                cursor.executemany(
                    "INSERT INTO vehicle_use_case_tags (vehicle_id, use_case_tag) VALUES (?, ?)",
                    tag_values
                )
            
            conn.commit()
            
            # Return the vehicle data (no need to query again, we already have it)
            vehicle = {
                'vehicle_id': vehicle_data['vehicle_id'],
                'make': vehicle_data['make'],
                'model': vehicle_data['model'],
                'trim': vehicle_data['trim'],
                'year': vehicle_data['year'],
                'price': vehicle_data['price'],
                'currency': vehicle_data['currency'],
                'mileage': vehicle_data['mileage'],
                'body_style': vehicle_data['body_style'],
                'transmission': vehicle_data['transmission'],
                'drivetrain': vehicle_data['drivetrain'],
                'powertrain_type': vehicle_data['powertrain_type'],
                'seating_capacity': vehicle_data['seating_capacity'],
                'color': vehicle_data['color'],
                'cargo_space': vehicle_data['cargo_space'],
                'has_hatch_access': vehicle_data['has_hatch_access'],
                'has_fold_flat_seats': vehicle_data['has_fold_flat_seats'],
                'fuel_economy': vehicle_data['fuel_economy'],
                'reliability': vehicle_data['reliability'],
                'city': vehicle_data['city'],
                'state_region': vehicle_data['state_region'],
                'zip_code': vehicle_data['zip_code'],
                'number_of_owners': vehicle_data['number_of_owners'],
                'features': vehicle_data['features'],
                'use_case_tags': vehicle_data['use_case_tags']
            }
            
            return vehicle
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"[{self.name}] ERROR: Failed to get/update sample vehicle: {e}")
            return None

