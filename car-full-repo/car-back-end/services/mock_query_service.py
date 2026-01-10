"""
Mock Query Service - Returns mock results without inference or database
Used for testing the application without GPU/inference capabilities.

This service accepts ONLY the following string inputs:
- "pass": Returns 1-10 random fake vehicle results
- "fail": Returns empty results (no results found)
- "insufficient": Returns a message indicating too many results, please rephrase
"""
import random
from typing import Dict, Any, List, Tuple
from schemas.vehicle_selection_v1_vocab import (
    BODY_STYLES, USE_CASE_TAGS, TRANSMISSIONS, DRIVETRAINS, 
    POWERTRAIN_TYPES, FEATURE_TAGS
)


class MockQueryService:
    """Mock service that returns fake results without inference or database"""
    
    def __init__(self):
        """Initialize the mock query service"""
        self.name = "mock-query-service"
        self.initialized = False
        
        # Extended vocabularies from schema
        self.makes = [
            'Toyota', 'Honda', 'Ford', 'Chevrolet', 'BMW', 'Mercedes-Benz',
            'Tesla', 'Audi', 'Subaru', 'Jeep', 'Nissan', 'Volkswagen',
            'Hyundai', 'Kia', 'Mazda', 'Lexus', 'Acura', 'Infiniti',
            'Cadillac', 'Lincoln', 'Volvo', 'Porsche', 'Jaguar', 'Land Rover'
        ]
        
        self.models = {
            'Toyota': ['Camry', 'Corolla', 'RAV4', 'Highlander', 'Prius', 'Tacoma', '4Runner'],
            'Honda': ['Accord', 'Civic', 'CR-V', 'Pilot', 'Odyssey', 'Ridgeline'],
            'Ford': ['F-150', 'Explorer', 'Escape', 'Mustang', 'Edge', 'Expedition'],
            'Chevrolet': ['Silverado', 'Equinox', 'Tahoe', 'Suburban', 'Malibu', 'Camaro', 'Corvette'],
            'BMW': ['3 Series', '5 Series', 'X3', 'X5', 'X7', 'M3'],
            'Mercedes-Benz': ['C-Class', 'E-Class', 'S-Class', 'GLC', 'GLE', 'GLS'],
            'Tesla': ['Model 3', 'Model Y', 'Model S', 'Model X'],
            'Audi': ['A4', 'A6', 'Q5', 'Q7', 'Q8'],
            'Subaru': ['Outback', 'Forester', 'Crosstrek', 'Ascent'],
            'Jeep': ['Grand Cherokee', 'Wrangler', 'Cherokee', 'Compass'],
            'Nissan': ['Altima', 'Sentra', 'Rogue', 'Pathfinder', 'Frontier'],
            'Volkswagen': ['Jetta', 'Passat', 'Atlas', 'Tiguan'],
            'Hyundai': ['Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Palisade'],
            'Kia': ['Optima', 'Sorento', 'Telluride', 'Sportage'],
            'Mazda': ['CX-5', 'CX-9', 'Mazda3', 'Mazda6'],
            'Lexus': ['ES', 'RX', 'GX', 'LX', 'IS'],
            'Acura': ['TLX', 'MDX', 'RDX'],
            'Infiniti': ['Q50', 'QX50', 'QX60', 'QX80'],
            'Cadillac': ['XT5', 'Escalade', 'CT5', 'CT6'],
            'Lincoln': ['Navigator', 'Aviator', 'Corsair'],
            'Volvo': ['XC40', 'XC60', 'XC90', 'S60', 'S90'],
            'Porsche': ['911', 'Cayenne', 'Macan', 'Panamera'],
            'Jaguar': ['F-Pace', 'XE', 'XF'],
            'Land Rover': ['Range Rover', 'Discovery', 'Defender']
        }
        
        self.trims = ['Base', 'LE', 'SE', 'XLE', 'Limited', 'Platinum', 'Sport', 'Luxury', 'Premium']
        self.colors = [
            'black', 'white', 'silver', 'gray', 'grey', 'red', 'blue', 'green',
            'brown', 'beige', 'tan', 'gold', 'orange', 'yellow', 'purple',
            'burgundy', 'maroon', 'navy', 'teal', 'pink'
        ]
        self.cities = [
            'Los Angeles', 'New York', 'Chicago', 'Houston', 'Phoenix',
            'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'
        ]
        self.states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'AZ', 'WA', 'GA', 'NC']
        self.zip_codes = ['90210', '10001', '77001', '33101', '85001', '19101', '98101', '30301', '28201']
    
    def register(self, app):
        """Register routes and functionality with the Flask app"""
        pass
    
    def initialize(self):
        """Initialize the service"""
        if not self.initialized:
            print(f"[{self.name}] Initializing...")
            print(f"[{self.name}] Mock mode: Accepts only 'pass', 'fail', or 'insufficient' strings")
            self.initialized = True
            print(f"[{self.name}] Initialized successfully")
    
    def process_query(self, query_text: str) -> Dict[str, Any]:
        """
        Process a mock query - accepts ONLY "pass", "fail", or "insufficient"
        
        Args:
            query_text: Must be exactly "pass", "fail", or "insufficient"
        
        Returns:
            Dict with 'success', 'query', 'results', 'result_count', and optional 'message'
        """
        query_text = query_text.strip().lower()
        
        if query_text == "pass":
            return self._generate_pass_response()
        elif query_text == "fail":
            return self._generate_fail_response()
        elif query_text == "insufficient":
            return self._generate_insufficient_response()
        else:
            raise ValueError(
                f"Mock query service accepts only 'pass', 'fail', or 'insufficient'. "
                f"Received: '{query_text}'. "
                f"See README-NOINFERENCE.md for usage instructions."
            )
    
    def _generate_pass_response(self) -> Dict[str, Any]:
        """Generate a successful response with 1-10 random vehicle results"""
        num_results = random.randint(1, 10)
        results = []
        
        for i in range(num_results):
            vehicle = self._generate_random_vehicle(i + 1)
            results.append(vehicle)
        
        return {
            'success': True,
            'query': 'pass',
            'extracted_fields': self._generate_extracted_fields(),
            'sql_query': f"SELECT * FROM vehicles WHERE make IN ('Toyota', 'Honda') LIMIT {num_results}",
            'sql_params': [],
            'results': results,
            'result_count': len(results),
            'quality_warnings': [],
            'quality_acceptable': True
        }
    
    def _generate_fail_response(self) -> Dict[str, Any]:
        """Generate a failed response with no results"""
        return {
            'success': True,
            'query': 'fail',
            'extracted_fields': {},
            'sql_query': "SELECT * FROM vehicles WHERE make = 'NonExistentMake'",
            'sql_params': [],
            'results': [],
            'result_count': 0,
            'quality_warnings': [],
            'quality_acceptable': True
        }
    
    def _generate_insufficient_response(self) -> Dict[str, Any]:
        """Generate an insufficient response with a message"""
        return {
            'success': False,
            'query': 'insufficient',
            'error': 'Too many results found that match your criteria. Please refine your search by adding more specific constraints (e.g., make, model, year range, budget range).',
            'error_type': 'insufficient_criteria',
            'extracted_fields': {},
            'sql_query': '',
            'sql_params': [],
            'results': [],
            'result_count': 0
        }
    
    def _generate_random_vehicle(self, index: int) -> Dict[str, Any]:
        """Generate a single random vehicle with values from schema enums"""
        make = random.choice(self.makes)
        model = random.choice(self.models.get(make, ['Model']))
        trim = random.choice(self.trims)
        
        # Random selection of array fields
        powertrain_count = random.randint(1, 3)
        powertrains = random.sample([p for p in POWERTRAIN_TYPES if p != 'unspecified'], powertrain_count)
        
        feature_count = random.randint(1, min(5, len(FEATURE_TAGS)))
        features = random.sample(FEATURE_TAGS, feature_count)
        
        use_case_count = random.randint(1, min(4, len(USE_CASE_TAGS)))
        use_cases = random.sample(USE_CASE_TAGS, use_case_count)
        
        return {
            'vehicle_id': f'mock_vehicle_{index:03d}',
            'make': make,
            'model': model,
            'trim': trim,
            'year': random.randint(2018, 2024),
            'price': random.randint(20000, 80000),
            'currency': 840,  # USD
            'mileage': random.randint(5000, 150000),
            'body_style': random.choice(BODY_STYLES),
            'transmission': random.choice([t for t in TRANSMISSIONS if t != 'unspecified']),
            'drivetrain': random.choice([d for d in DRIVETRAINS if d != 'unspecified']),
            'powertrain_types': powertrains,
            'seating_capacity': random.choice([2, 4, 5, 7, 8, 12]),
            'color': random.choice(self.colors),
            'cargo_space': random.choice(['none', 'low', 'medium', 'high', 'unknown']),
            'has_hatch_access': random.choice([0, 1]),
            'has_fold_flat_seats': random.choice([0, 1]),
            'fuel_economy': random.choice(['low', 'medium', 'high', 'unknown']),
            'reliability': random.choice(['low', 'medium', 'high', 'unknown']),
            'city': random.choice(self.cities),
            'state_region': random.choice(self.states),
            'zip_code': random.choice(self.zip_codes),
            'number_of_owners': random.randint(1, 5),
            'features': features,
            'use_case_tags': use_cases
        }
    
    def _generate_extracted_fields(self) -> Dict[str, Any]:
        """Generate extracted fields that would normally come from model inference"""
        return {
            'mk': random.sample(self.makes, random.randint(1, 3)),
            'vt': {
                'inc': random.sample(BODY_STYLES, random.randint(1, 2))
            },
            'oc': {
                'bud': {
                    'max': random.randint(30000, 60000)
                }
            }
        }
