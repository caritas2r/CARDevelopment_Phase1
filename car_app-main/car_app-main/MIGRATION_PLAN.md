# Migration Plan: Supabase → Flask Backend

## Overview
This document outlines the plan to migrate car_app-main from Supabase to the Flask backend in car-full-repo.

## Key Changes

### 1. Remove Supabase Dependencies
- Remove `@supabase/supabase-js` from package.json
- Remove supabase folder (functions, migrations)
- Remove environment variables for Supabase

### 2. Create Flask API Client
- Replace `src/lib/supabase.ts` with `src/lib/api.ts` (Flask backend client)
- Remove Supabase-specific API calls
- Create simple API client for `/api/query/v1` endpoint

### 3. Simplify Authentication
- Remove or simplify authentication (Flask backend has no auth)
- Update `useAuth.ts` to return mock/empty user or remove auth entirely
- Update `RequireAuth.tsx` to allow all users or remove auth wrapper
- Update `SignIn.tsx` - either remove or make it a simple landing page

### 4. Replace Query Functionality
- **NewRequest.tsx**: Replace complex sourcing form with simple query input
- Use `/api/query/v1` endpoint instead of Supabase Edge Functions
- **Candidates.tsx**: Display results from Flask backend instead of Supabase
- Remove all Supabase database queries

### 5. Update Other Pages
- **Landing.tsx**: Remove auth checks or simplify
- **Build/Concierge/Billing/Admin**: Either remove or stub out (no backend support yet)
- Remove all Supabase imports and calls

### 6. Flask Backend API
The Flask backend provides:
- `POST /api/query/v1` - Simple natural language query endpoint
  - Request: `{ "query": "natural language text" }`
  - Response: `{ "success": true, "results": [...], "result_count": N, ... }`

## Implementation Order
1. Create Flask API client
2. Update package.json (remove Supabase)
3. Simplify authentication
4. Replace NewRequest.tsx (sourcing form → simple query)
5. Replace Candidates.tsx (display Flask results)
6. Update other pages/components
7. Remove Supabase folder and clean up
8. Update environment variables

