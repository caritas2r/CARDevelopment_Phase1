# End-to-End Pipeline: Complete Application Flow

This document describes the complete flow from when a user submits a natural language query through the frontend, the backend processing pipeline, results display, payment processing, and feedback submission.

## Complete Application Flow Overview

```
User Query → Frontend Query Page → Backend API → Inference Pipeline → Database Query → Results → Frontend Results Page → Payment (Optional) → Feedback (Optional)
```

## Step-by-Step Complete Flow

### 1. User Query Submission (Frontend Query Page)

**File**: `car-front-end/src/containers/query-page/index.js`

**What Happens**:
- User types natural language query in textarea (e.g., "I want a Toyota Venza Hybrid, under $35k, with cloth seats but premium audio")
- User clicks "Submit Query" button or presses Enter
- Frontend validates input is not empty
- Frontend displays loading indicator: "Processing query..."
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

### 2. Backend Query Processing Pipeline

**File**: `car-back-end/services/query_service.py`

The backend receives the query and processes it through the following pipeline:

#### 2.1 Query Validation
- Validates request body contains `query` field
- Validates query is non-empty string

#### 2.2 Mock Mode vs Full Pipeline

**Mock Mode** (when `--noinference` flag is used):
- Uses `MockQueryService` which accepts only: "pass", "fail", or "insufficient"
- Returns predefined responses for testing without GPU/model dependencies

**Full Pipeline Mode**:

**Step 1: Inference Service** - NLP → JSON (Shortened Keys)
**File**: `car-back-end/services/inference_service.py`
- Processes natural language query through trained model (Qwen2.5-3B with LoRA adapters)
- Tokenizes input text
- Runs inference through model
- Model generates JSON with shortened keys (mk, md, vt, etc.)
- Parses JSON from model output (stops at `<END_JSON>` marker)
- Returns structured JSON dictionary

**Step 2: Key Mapping Service** - Expand Shortened Keys
**File**: `car-back-end/services/key_mapping_service.py`
- Expands shortened keys to full keys:
  - `mk` → `make`
  - `md` → `model`
  - `vt` → `vehicle_type`
  - `oc` → `ownership_constraints`
  - etc.
- Returns JSON with full keys

**Step 3: JSON Input Converter Service** - JSON → SQL
**File**: `car-back-end/services/json_input_converter_service.py`
- Converts structured JSON to SQL query
- Processes all constraints (make, model, price, features, etc.)
- Builds WHERE clause with appropriate operators (IN, =, <=, >=, EXISTS)
- Handles junction tables for many-to-many relationships
- Returns SQL query string and parameter list

**Step 4: Database Query Service** - Execute SQL
**File**: `car-back-end/services/database_query_service.py`
- Executes parameterized SQL query
- Fetches results from database
- Converts rows to list of dictionaries
- Returns vehicle records

**Step 5: Output Quality Service** - Quality Checks
**File**: `car-back-end/services/output_quality_service.py`
- Validates output quality
- Checks for empty/malformed JSON
- Detects contradictory constraints
- Returns quality warnings (non-blocking)

---

### 3. Backend Response to Frontend

**File**: `car-back-end/services/query_service.py`

The backend formats and returns a JSON response:

**Success Response** (with results):
```json
{
    "success": true,
    "query": "I want a Toyota Venza Hybrid, under $35k, with cloth seats but premium audio",
    "extracted_fields": {...},
    "sql_query": "SELECT * FROM vehicles WHERE make IN (?) AND price <= ? ...",
    "sql_params": ["Toyota", 35000, ...],
    "results": [
        {
            "vehicle_id": 1,
            "make": "Toyota",
            "model": "Venza",
            "year": 2023,
            "price": 32000,
            "body_style": "crossover",
            ...
        },
        ...
    ],
    "result_count": 5,
    "quality_warnings": [],
    "quality_acceptable": true
}
```

**Insufficient Criteria Response**:
```json
{
    "success": false,
    "query": "insufficient",
    "error": "Too many results found that match your criteria. Please refine your search...",
    "error_type": "insufficient_criteria",
    "extracted_fields": {},
    "sql_query": "",
    "results": [],
    "result_count": 0
}
```

**Failure Response** (query processing error):
```json
{
    "success": false,
    "query": "invalid query text",
    "error": "Unable to process query.",
    "error_type": "processing_error",
    "extracted_fields": {},
    "sql_query": "",
    "results": [],
    "result_count": 0
}
```

---

### 4. Frontend Response Handling (Query Page)

**File**: `car-front-end/src/containers/query-page/index.js`

The frontend handles three possible response scenarios:

#### 4.1 Success Response (Results Found)
- Stores query results in `sessionStorage`:
  - `queryResults`: Full response data
  - `lastQueryText`: Original query text
  - `lastQueryData`: Response data (for feedback)
- Redirects to results page: `window.location.hash = '#/results'`

#### 4.2 Insufficient Criteria Response (Warning)
- Displays warning UI with yellow/orange styling:
  - Status: "Query not processed"
  - Message: "Warning: Insufficient criteria detected, please refine your search parameters."
- Shows "Results Not Satisfactory" button
- Stores query data in `sessionStorage` for potential feedback submission
- User can click button to submit feedback

#### 4.3 Failure Response (Error)
- Displays error UI with red styling:
  - Status: "Error submitting query"
  - Message: "Error: Unable to process query."
- Shows "Results Not Satisfactory" button
- Stores query data in `sessionStorage` for potential feedback submission
- User can click button to submit feedback

---

### 5. Results Page Display

**File**: `car-front-end/src/containers/results-page/index.js`

**What Happens**:
- Retrieves results from `sessionStorage`
- Checks if payment has been completed (`paymentCompleted` flag)
- Splits results into:
  - **Free Results**: First 2 vehicles (fully visible)
  - **Premium Results**: Remaining vehicles (blurred with paywall overlay)

**Display Features**:
- Shows query text and result count
- Displays extracted fields and generated SQL in sidebar
- Renders vehicle cards with:
  - Make, Model, Year
  - Price, Mileage
  - Body Style, Transmission, Drivetrain
  - Powertrain Types
  - Features and Use Case Tags
  - Location information
- Shows "Results Not Satisfactory" button
- If premium results exist, shows blurred overlay with payment prompt

**Paywall Functionality**:
- If `paymentCompleted === false` and there are premium results:
  - First 2 results are fully visible
  - Remaining results are blurred
  - Overlay message: "Unlock all results for $9.99"
  - Clicking overlay navigates to payment page

---

### 6. Payment Processing Flow

**File**: `car-front-end/src/containers/payment-page/index.js`  
**Backend File**: `car-back-end/services/payment_service.py`

#### 6.1 Payment Page Display
- Shows payment form with fields:
  - Card Number (formatted with spaces)
  - Expiry Date (MM/YY format)
  - CVV
  - Cardholder Name
- Displays amount: $9.99
- Shows note: "Secure payment processing via Stripe (sandbox/test mode)"

#### 6.2 Payment Submission
- User fills in payment form (validation for UX only - actual card data not sent)
- User clicks "Pay $9.99" button
- Frontend displays debug info showing:
  - Payment Method ID: `pm_card_visa` (Stripe test PaymentMethod)
  - Amount: $9.99 (999 cents)
  - Currency: USD
- Frontend makes POST request to backend:

```javascript
fetch(`${API_BASE_URL}/api/payment/process`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        amount: 999,
        currency: 'usd',
        payment_method: 'pm_card_visa'
    })
})
```

#### 6.3 Backend Payment Processing
- `PaymentService` receives request
- Validates `STRIPE_API_KEY` is configured (loaded from `env_var` file)
- Creates Stripe `PaymentIntent` with:
  - Amount: 999 cents ($9.99)
  - Currency: USD
  - Payment Method: `pm_card_visa` (test PaymentMethod)
  - Confirmation: automatic
- Stripe processes payment (sandbox/test mode)
- Returns success or error response

#### 6.4 Payment Success Response
```json
{
    "success": true,
    "message": "Payment processed successfully",
    "payment_intent_id": "pi_xxx",
    "amount": 999,
    "currency": "usd"
}
```

#### 6.5 Frontend Payment Success Handling
- Sets `sessionStorage.setItem('paymentCompleted', 'true')`
- Displays success message: "Payment successful! Redirecting..."
- Redirects to results page: `window.location.hash = '#/results'`

#### 6.6 Results Page After Payment
- Checks `paymentCompleted === true`
- Shows all results (no blur, no paywall)
- Displays: "Showing all X results (Unlocked)"

---

### 7. Feedback Submission Flow

Users can submit feedback when results are unsatisfactory through the "Results Not Satisfactory" button.

#### 7.1 Feedback Button Locations
- **Query Page**: Available when query fails or is insufficient
- **Results Page**: Always available after results are displayed

#### 7.2 Feedback Submission Process

**Frontend** (`query-page/index.js` or `results-page/index.js`):
1. User clicks "Results Not Satisfactory" button
2. Frontend prompts user for optional reason
3. Retrieves data from `sessionStorage`:
   - `lastQueryText`: Original query text
   - `lastQueryData`: Full response data
4. Makes POST request to backend:

```javascript
fetch(`${API_BASE_URL}/api/query/feedback`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        query: queryText,
        extracted_fields: queryData.extracted_fields || {},
        sql_query: queryData.sql_query || '',
        reason: reason || ''
    })
})
```

#### 7.3 Backend Feedback Processing

**File**: `car-back-end/services/query_service.py`

**What Happens**:
1. Receives feedback data
2. Determines `query_status`:
   - `'pass'`: If prompt is "pass" or `success: true` with `result_count > 0`
   - `'fail'`: If prompt is "fail" or `success: false`
   - `'insufficient'`: If prompt is "insufficient" or `success: true` with `result_count === 0`
3. Stores feedback in `flagged_prompts` database table:
   - `prompt_text`: Original query
   - `flagged_annotation`: JSON string of extracted fields
   - `flagged_query`: Generated SQL query
   - `flag_reason`: User-provided reason (optional)
   - `query_status`: Status ('pass', 'fail', or 'insufficient')
4. Returns success response with `flagged_id`

**Database Schema**:
```sql
CREATE TABLE flagged_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_text TEXT NOT NULL,
    flagged_annotation TEXT,
    flagged_query TEXT,
    flag_reason TEXT,
    query_status TEXT
);
```

#### 7.4 Feedback Success Response
```json
{
    "success": true,
    "message": "Feedback stored successfully",
    "flagged_id": 123
}
```

#### 7.5 Frontend Feedback Success Handling
- Updates button text to "Feedback Submitted"
- Disables button to prevent double-submission
- Shows confirmation message

---

## Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND QUERY PAGE                           │
│  - User enters query                                             │
│  - Submits to backend                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │ POST /api/query/v1
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND QUERY SERVICE                         │
│  1. InferenceService: NLP → JSON (shortened keys)               │
│  2. KeyMappingService: Expand keys                               │
│  3. JsonInputConverterService: JSON → SQL                       │
│  4. DatabaseQueryService: Execute SQL                            │
│  5. OutputQualityService: Quality checks                         │
└────────────────────────┬────────────────────────────────────────┘
                         │ JSON Response
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FRONTEND RESPONSE HANDLING                      │
│  - Success: Store results → Navigate to results page            │
│  - Insufficient: Show warning + feedback button                 │
│  - Failure: Show error + feedback button                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌──────────────────────┐      ┌──────────────────────┐
│   RESULTS PAGE       │      │   FEEDBACK SUBMIT    │
│  - Display results   │      │   POST /api/query/   │
│  - Paywall (if any)  │      │   feedback           │
│  - Feedback button   │      │   → flagged_prompts  │
└──────────┬───────────┘      └──────────────────────┘
           │
           │ Click paywall
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND PAYMENT PAGE                         │
│  - Payment form (UX only - not sent)                            │
│  - Submit payment                                                │
└────────────────────────┬────────────────────────────────────────┘
                         │ POST /api/payment/process
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND PAYMENT SERVICE                       │
│  - Stripe PaymentIntent.create()                                │
│  - Process with pm_card_visa (test)                             │
└────────────────────────┬────────────────────────────────────────┘
                         │ Success Response
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              RESULTS PAGE (AFTER PAYMENT)                        │
│  - All results visible (unlocked)                                │
│  - Payment completed flag set                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Query Status Determination

The system determines query status based on the response:

1. **Pass** (`query_status: 'pass'`):
   - Query processed successfully AND results found (`success: true` AND `result_count > 0`)
   - Example: User searches for "Toyota Camry" and finds matching vehicles

2. **Fail** (`query_status: 'fail'`):
   - Query failed to process (`success: false`)
   - Example: Query parsing error, inference error, or SQL execution error

3. **Insufficient** (`query_status: 'insufficient'`):
   - Query processed successfully BUT no results found (`success: true` AND `result_count === 0`)
   - Example: User searches for "McLaren P1" but no such vehicle exists in database

---

## Mock Mode Behavior

When running with `--noinference` flag (no GPU/model dependencies):

**Mock Query Service** accepts only three exact string values:
- `"pass"` - Returns 1-10 random fake vehicle results
- `"fail"` - Returns empty results (triggers failure UI)
- `"insufficient"` - Returns error response (triggers insufficient warning UI)

All mock responses use realistic data from Vehicle Selection V1 schema enums.

---

## Environment Configuration

### Stripe Payment Configuration

**File**: `env_var` (in repository root)
```
API_KEY = sk_test_xxx
```

The `create-venv.bat` script:
1. Reads `API_KEY` from `env_var` file
2. Sets `STRIPE_API_KEY` environment variable
3. Passes to backend process

If `STRIPE_API_KEY` is not configured, payment processing returns a 503 error.

---

## Error Handling

The pipeline includes error handling at multiple levels:

1. **Frontend Query Page**:
   - Validates empty queries
   - Handles network errors
   - Displays appropriate UI for success/warning/error states

2. **Backend Query Service**:
   - Validates request format
   - Catches exceptions at each pipeline step
   - Returns structured error responses

3. **Backend Payment Service**:
   - Validates API key configuration
   - Handles Stripe API errors (card errors, rate limits, etc.)
   - Returns appropriate HTTP status codes

4. **Database Operations**:
   - Handles SQL execution errors
   - Manages connection errors
   - Validates schema on startup

---

## Current Implementation Status

### ✅ Fully Implemented
- Frontend query submission with status handling
- Frontend results page with paywall
- Frontend payment page with Stripe integration
- Frontend feedback submission (query page and results page)
- Backend query processing pipeline
- Backend payment processing with Stripe
- Backend feedback storage in database
- Query status determination (pass/fail/insufficient)
- Mock mode for testing without GPU
- Database schema validation and migration

### 🔄 Partial Implementation
- **InferenceService**: Currently uses mock implementation; full model inference needs to be implemented

---

## Key Files Reference

**Frontend**:
- `car-front-end/src/containers/query-page/index.js` - Query submission and response handling
- `car-front-end/src/containers/results-page/index.js` - Results display with paywall
- `car-front-end/src/containers/payment-page/index.js` - Payment processing
- `car-front-end/app.js` - Routing between pages

**Backend**:
- `car-back-end/services/query_service.py` - Query orchestration and feedback endpoint
- `car-back-end/services/inference_service.py` - NLP to JSON conversion
- `car-back-end/services/payment_service.py` - Stripe payment processing
- `car-back-end/utils/db_bootstrap.py` - Database schema (includes `flagged_prompts` table)
- `car-back-end/app.py` - Flask app initialization and service registration

**Configuration**:
- `env_var` - Stripe API key configuration
- `create-venv.bat` - Application launcher with environment setup

---

## Next Steps

To complete the pipeline:

1. **Implement Full Inference Service**:
   - Load trained model (Qwen2.5-3B with LoRA adapters)
   - Implement tokenization and inference
   - Handle stopping criteria (`<END_JSON>` marker)
   - Parse and validate JSON output

2. **Production Considerations**:
   - Replace Stripe test PaymentMethod with real payment flow
   - Add payment webhooks for confirmation
   - Implement payment receipt generation
   - Add user authentication/authorization
   - Implement rate limiting
   - Add logging and monitoring
