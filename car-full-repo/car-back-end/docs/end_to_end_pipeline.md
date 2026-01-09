# End-to-End Pipeline: Natural Language Query to SQL Execution

This document traces the complete flow from when a user submits a natural language query on the frontend through to SQL query execution and results returned.

## Pipeline Overview

```
Frontend → Flask API → QueryService → InferenceService → KeyMappingService → JsonInputConverterService → DatabaseQueryService → Database → Results
```

## Step-by-Step Flow

### 1. Frontend Submission
**File**: `car-front-end/src/containers/query-page/index.js`

**Location**: Lines 138-170

**What Happens**:
- User types natural language query in textarea (e.g., "I want a Toyota Venza Hybrid, under $35k, with cloth seats but premium audio")
- User clicks "Submit Query" button or presses Enter
- Frontend validates input is not empty
- Frontend makes POST request to backend:

```javascript
const response = await fetch(`${API_BASE_URL}/api/query/v1`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query: queryText })
});
```

**Request Body**:
```json
{
    "query": "I want a Toyota Venza Hybrid, under $35k, with cloth seats but premium audio"
}
```

---

### 2. Flask API Route Registration
**File**: `car-back-end/app.py`

**Location**: Lines 15-59

**What Happens**:
- Flask app is created via `create_app()`
- All services are instantiated and registered:
  - `InferenceService` - Converts NLP to JSON
  - `KeyMappingService` - Expands shortened keys
  - `JsonInputConverterService` - Converts JSON to SQL
  - `DatabaseQueryService` - Executes SQL queries
  - `QueryService` - Orchestrates the pipeline
- Services are initialized
- Flask app returns with all routes registered

**Key Service Dependencies**:
```python
query_service = QueryService(
    inference_service=inference_service,
    key_mapping_service=key_mapping_service,
    json_converter_service=json_converter_service,
    database_query_service=db_query_service,
    mock_nlp_trip_service=mock_nlp_trip_service
)
```

---

### 3. QueryService Endpoint Handler
**File**: `car-back-end/services/query_service.py`

**Location**: Lines 36-125

**What Happens**:
- Flask route `/api/query/v1` receives POST request
- Validates request body contains `query` field
- Validates query is non-empty string
- **Note**: Currently has PoC mode that returns mock data if `mock_nlp_trip_service` is enabled
- If PoC mode is disabled, proceeds to full pipeline:

**Pipeline Steps** (Lines 87-112):
```python
# Step 1: Process through inference service (NLP -> JSON with shortened keys)
json_with_short_keys = self.inference_service.process_query(query_text)

# Step 2: Expand shortened keys to full keys (mk -> make, md -> model, etc.)
json_with_full_keys = self.key_mapping_service.expand_shortened_keys(json_with_short_keys)

# Step 3: Convert JSON to SQL
sql_query, sql_params = self.json_converter_service.convert_to_sql(json_with_full_keys)

# Step 4: Execute query
results = self.database_query_service.execute_query(sql_query, sql_params)

# Step 5: Format and return results
return jsonify({
    'success': True,
    'query': query_text,
    'results': results,
    'result_count': len(results) if results else 0
}), 200
```

---

### 4. InferenceService: NLP → JSON (Shortened Keys)
**File**: `car-back-end/services/inference_service.py`

**Location**: Lines 32-99

**What Happens**:
- `process_query(query_text)` is called with natural language string
- **Current Status**: Method is `NotImplementedError` - needs to be implemented
- **Expected Behavior**: 
  - Load trained model (e.g., Qwen2.5-3B with LoRA adapters)
  - Tokenize input text
  - Run inference through model
  - Model generates JSON with shortened keys (mk, md, vt, etc.)
  - Parse JSON from model output (stops at `<END_JSON>` marker)
  - Return structured JSON dictionary

**Example Input**:
```
"I want a Toyota Venza Hybrid, under $35k, with cloth seats but premium audio"
```

**Example Output** (with shortened keys):
```json
{
    "mk": ["Toyota"],
    "md": ["Venza"],
    "tr": "unspecified",
    "vt": {"inc": ["unspecified"], "exc": ["unspecified"]},
    "cp": {"seat_min": "unspecified", "kids": "unspecified", "pets": "unspecified", "cargo_pri": "unspecified", "cargo_fx": {"hatch": "unspecified", "foldflat": "unspecified"}},
    "iu": {"tags": ["unspecified"]},
    "pd": {"tx": "unspecified", "dt": "unspecified", "pt": ["hybrid", "plug_in_hybrid", "mild_hybrid"], "fe_pri": "unspecified"},
    "fa": {"must": ["cloth_seats"], "nice": ["premium_audio"], "avoid": ["unspecified"]},
    "oc": {"bud": {"cur": 840, "min": "unspecified", "max": 35000, "max_strict": "true"}, "yr": {"min": "unspecified", "max": "unspecified"}, "mi": {"max": "unspecified", "qual": ["unspecified"]}, "owners": "unspecified"},
    "ps": {"rel_pri": "unspecified", "clr": ["unspecified"]},
    "lc": {"cty": "unspecified", "st": "unspecified", "rad": "unspecified"}
}
```

---

### 5. KeyMappingService: Expand Shortened Keys
**File**: `car-back-end/services/key_mapping_service.py`

**Location**: Lines 124-142

**What Happens**:
- `expand_shortened_keys(json_with_short_keys)` is called
- Recursively traverses JSON structure
- Maps shortened keys to full keys using `SHORT_TO_FULL_MAPPING`:
  - `mk` → `make`
  - `md` → `model`
  - `vt` → `vehicle_type`
  - `oc` → `ownership_constraints`
  - `bud` → `budget`
  - etc.
- Returns JSON with full keys

**Example Input** (shortened keys):
```json
{
    "mk": ["Toyota"],
    "oc": {"bud": {"max": 35000}}
}
```

**Example Output** (full keys):
```json
{
    "make": ["Toyota"],
    "ownership_constraints": {"budget": {"max": 35000}}
}
```

---

### 6. JsonInputConverterService: JSON → SQL
**File**: `car-back-end/services/json_input_converter_service.py`

**Location**: Lines 270-302

**What Happens**:
- `convert_to_sql(json_with_full_keys)` is called
- Uses declarative mappings (`INCLUSION_MAPPINGS` and `EXCLUSION_MAPPINGS`) to build SQL
- Processes JSON structure to extract:
  - Identity fields (make, model, trim, year)
  - Vehicle type constraints (body_style)
  - Capacity/practicality (seating, cargo)
  - Use case tags (via junction table)
  - Powertrain (transmission, drivetrain, powertrain_type)
  - Features (via junction table)
  - Ownership constraints (budget, mileage, owners)
  - Location constraints
- Builds WHERE clause with appropriate operators (IN, =, <=, >=, EXISTS)
- Handles junction tables for many-to-many relationships (features, use_case_tags, powertrain_types)
- Returns SQL query string and parameter list

**Example Input** (full keys):
```json
{
    "make": ["Toyota"],
    "model": ["Venza"],
    "powertrain_drivability": {
        "powertrain_type": ["hybrid", "plug_in_hybrid", "mild_hybrid"]
    },
    "features_amenities": {
        "must_have": ["cloth_seats"]
    },
    "ownership_constraints": {
        "budget": {
            "max": 35000,
            "strict_max": "true"
        }
    }
}
```

**Example Output**:
```python
sql_query = """
SELECT * FROM vehicles 
WHERE make IN (?) 
AND model IN (?) 
AND EXISTS (
    SELECT 1 FROM vehicle_powertrain_types jt 
    WHERE jt.vehicle_id = vehicles.vehicle_id 
    AND jt.powertrain_type IN (?,?,?)
) 
AND EXISTS (
    SELECT 1 FROM vehicle_features jt 
    WHERE jt.vehicle_id = vehicles.vehicle_id 
    AND jt.feature_tag IN (?)
) 
AND price <= ?
"""

sql_params = ["Toyota", "Venza", "hybrid", "plug_in_hybrid", "mild_hybrid", "cloth_seats", 35000]
```

---

### 7. DatabaseQueryService: Execute SQL
**File**: `car-back-end/services/database_query_service.py`

**Location**: Lines 47-80

**What Happens**:
- `execute_query(sql_query, sql_params)` is called
- Gets database connection from `DatabaseConnectionService`
- Creates cursor
- Executes parameterized SQL query with params (prevents SQL injection)
- Fetches all results
- Converts rows to list of dictionaries (column names as keys)
- Returns results list
- Closes cursor

**Example Execution**:
```python
cursor.execute(sql_query, sql_params)
# sql_query: "SELECT * FROM vehicles WHERE make IN (?) AND price <= ?"
# sql_params: ["Toyota", 35000]

rows = cursor.fetchall()
# Returns: [(1, "Toyota", "Venza", 2023, 32000, ...), ...]

# Convert to dictionaries
results = [
    {"vehicle_id": 1, "make": "Toyota", "model": "Venza", "year": 2023, "price": 32000, ...},
    ...
]
```

---

### 8. Results Returned to Frontend
**File**: `car-back-end/services/query_service.py`

**Location**: Lines 107-112

**What Happens**:
- QueryService formats response as JSON
- Returns HTTP 200 with results

**Response Format**:
```json
{
    "success": true,
    "query": "I want a Toyota Venza Hybrid, under $35k, with cloth seats but premium audio",
    "results": [
        {
            "vehicle_id": 1,
            "make": "Toyota",
            "model": "Venza",
            "year": 2023,
            "price": 32000,
            "body_style": "crossover",
            "transmission": "cvt",
            "drivetrain": "AWD",
            ...
        },
        ...
    ],
    "result_count": 5
}
```

**Frontend Display** (Lines 178-219):
- Frontend receives response
- Displays success status
- Renders vehicle results with details:
  - Make, Model, Year
  - Price, Mileage
  - Body Style, Transmission, Drivetrain
  - Powertrain Types
  - Seating Capacity
  - Color
  - Features
  - Use Case Tags

---

## Current Implementation Status

### ✅ Implemented
- Frontend query submission
- Flask API route registration
- QueryService orchestration
- KeyMappingService (key expansion)
- JsonInputConverterService (JSON to SQL conversion)
- DatabaseQueryService (SQL execution)
- Results formatting and return

### ⚠️ Needs Full Implementation
- **InferenceService.process_query()** - Currently has skeleton/mock implementation
  - **Current Status**: Returns mock JSON with basic keyword extraction for testing
  - **Needs Full Implementation**:
    1. Load trained model (Qwen2.5-3B with LoRA adapters) in `initialize()`
    2. Cache model in memory for fast inference
    3. Tokenize input text
    4. Run inference through model
    5. Handle stopping criteria (`<END_JSON>` marker)
    6. Parse JSON from model output
    7. Validate JSON structure
    8. Return structured JSON with shortened keys
  - **Mock Implementation**: Currently uses `_mock_process_query()` which extracts basic keywords (budget, vehicle type, drivetrain, use cases) for pipeline testing

### 🔄 Optional (PoC Mode)
- MockNlpTripService - Returns sample vehicle for testing without inference

---

## Error Handling

The pipeline includes error handling at multiple levels:

1. **Frontend**: Validates empty queries, handles network errors
2. **QueryService**: Validates request format, catches exceptions
3. **InferenceService**: Should validate input, handle model errors
4. **JsonInputConverterService**: Validates JSON structure, raises `ValueError` if no conditions
5. **DatabaseQueryService**: Catches SQL execution errors, raises exceptions

---

## Data Flow Summary

```
User Input (String)
    ↓
InferenceService.process_query()
    → JSON with Shortened Keys (mk, md, vt, etc.)
    ↓
KeyMappingService.expand_shortened_keys()
    → JSON with Full Keys (make, model, vehicle_type, etc.)
    ↓
JsonInputConverterService.convert_to_sql()
    → SQL Query String + Parameters
    ↓
DatabaseQueryService.execute_query()
    → List of Dictionaries (vehicle records)
    ↓
QueryService formats response
    → JSON Response
    ↓
Frontend displays results
```

---

## Next Steps

To complete the pipeline:

1. **Implement InferenceService.process_query()**:
   - Load model from checkpoint
   - Implement tokenization
   - Implement inference with stopping criteria (`<END_JSON>`)
   - Parse and validate JSON output
   - Handle errors gracefully

2. **Test End-to-End**:
   - Test with real queries
   - Verify SQL generation accuracy
   - Verify database query results
   - Test error cases

3. **Performance Optimization**:
   - Model loading (cache model in memory)
   - Query optimization
   - Response caching (if applicable)

