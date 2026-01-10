# Query Feedback Endpoint

## Overview

The feedback endpoint (`/api/query/feedback`) allows users to submit unsatisfactory query results for later training and model improvement.

## Purpose

This endpoint collects problematic queries that can be:
- Reviewed manually
- Annotated and added to training data
- Used to identify patterns in model failures
- Retrained into the model to improve performance

## Endpoint

**POST** `/api/query/feedback`

### Request Body

```json
{
  "query": "original query text",
  "extracted_fields": {...},
  "sql_query": "SELECT ...",
  "sql_params": [...],
  "reason": "optional reason why unsatisfactory"
}
```

**Required Fields:**
- `query` (string): The original natural language query

**Optional Fields:**
- `extracted_fields` (object): The extracted fields from model inference
- `sql_query` (string): The generated SQL query
- `sql_params` (array): The SQL parameters
- `reason` (string): User-provided reason why results were unsatisfactory

### Response

**Success (200 OK):**
```json
{
  "success": true,
  "message": "Feedback stored successfully"
}
```

**Error (400 Bad Request):**
```json
{
  "success": false,
  "error": "Missing required field: query",
  "error_type": "validation"
}
```

**Error (500 Internal Server Error):**
```json
{
  "success": false,
  "error": "error message",
  "error_type": "internal_error"
}
```

## Storage

Feedback is stored in:
```
car-back-end/training/data/feedback/unsatisfactory_queries.csv
```

### CSV Format

The CSV file contains the following columns:
- `timestamp`: ISO format timestamp when feedback was submitted
- `query`: Original query text
- `extracted_fields`: JSON string of extracted fields
- `sql_query`: Generated SQL query
- `sql_params`: JSON string of SQL parameters
- `reason`: User-provided reason (optional)

### Example CSV Entry

```csv
timestamp,query,extracted_fields,sql_query,sql_params,reason
2024-01-15T10:30:00,"show me corvettes",{"mk":["Cadillac"]},"SELECT * FROM vehicles WHERE make IN (?)","["Cadillac"]","Model returned wrong make - asked for corvette but got Cadillac"
```

## Frontend Integration

The frontend includes a "⚠️ Results Not Satisfactory" button on the results page that:
1. Prompts the user for an optional reason
2. Submits the feedback to this endpoint
3. Shows a confirmation message
4. Disables the button temporarily to prevent double-submission

### Usage Flow

1. User submits a query and receives results
2. User reviews results and finds them unsatisfactory
3. User clicks "⚠️ Results Not Satisfactory" button
4. User optionally provides a reason
5. Feedback is stored for later review/training

## Processing Feedback Data

To process collected feedback:

1. **Review Feedback:**
   ```bash
   cat car-back-end/training/data/feedback/unsatisfactory_queries.csv
   ```

2. **Add to Training Data:**
   - Review each unsatisfactory query
   - Annotate with correct expected output
   - Add to `training/data/active/unannotated_nlp_prompts.csv`
   - Re-annotate and retrain the model

3. **Analyze Patterns:**
   - Identify common failure modes
   - Look for systematic issues (e.g., specific makes/models, query types)
   - Use insights to improve training data or model architecture

## Notes

- The feedback directory is created automatically if it doesn't exist
- Feedback is appended to the CSV file (never overwritten)
- No limit on the number of feedback submissions
- Feedback data can be manually reviewed and cleaned before adding to training data
