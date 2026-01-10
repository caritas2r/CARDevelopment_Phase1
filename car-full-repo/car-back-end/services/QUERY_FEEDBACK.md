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

Feedback is stored in the `flagged_prompts` table in the SQLite database.

### Database Schema

The `flagged_prompts` table contains the following columns:
- `id`: Primary key (auto-increment)
- `prompt_text`: Original query text
- `flagged_annotation`: JSON string of extracted fields
- `flagged_query`: Generated SQL query
- `flag_reason`: User-provided reason (optional)
- `query_status`: Status of the query ('pass', 'fail', or 'insufficient')

### Example Database Entry

```sql
INSERT INTO flagged_prompts (prompt_text, flagged_annotation, flagged_query, flag_reason, query_status)
VALUES (
  'show me corvettes',
  '{"mk":["Cadillac"]}',
  'SELECT * FROM vehicles WHERE make IN (?)',
  'Model returned wrong make - asked for corvette but got Cadillac',
  'fail'
);
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
   Query the `flagged_prompts` table in the database:
   ```sql
   SELECT * FROM flagged_prompts;
   ```

2. **Add to Training Data:**
   - Review each unsatisfactory query
   - Annotate with correct expected output
   - Add to `training/data/active/unannotated_nlp_prompts.csv`
   - Re-annotate and retrain the model

3. **Analyze Patterns:**
   - Identify common failure modes by querying `query_status` and `flag_reason`
   - Look for systematic issues (e.g., specific makes/models, query types)
   - Use insights to improve training data or model architecture

## Notes

- Feedback is stored in the database `flagged_prompts` table
- The table schema is automatically created and validated on application startup
- No limit on the number of feedback submissions
- Feedback data can be manually reviewed and cleaned before adding to training data
- The `query_status` field indicates whether the query was 'pass', 'fail', or 'insufficient'
