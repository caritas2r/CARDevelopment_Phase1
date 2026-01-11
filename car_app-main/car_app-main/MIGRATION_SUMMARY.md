# Migration Summary: Supabase → Flask Backend

## Completed Changes

### 1. ✅ Removed Supabase Dependencies
- Removed `@supabase/supabase-js` from `package.json`
- Created new Flask API client in `src/lib/api.ts`

### 2. ✅ Simplified Authentication
- Updated `src/hooks/useAuth.ts` to return mock user (no real auth needed)
- Updated `src/pages/auth/RequireAuth.tsx` to allow all users (no auth check)
- Updated `src/pages/auth/SignIn.tsx` to just redirect to home
- Updated `src/pages/Landing.tsx` to work without auth

### 3. ✅ Replaced Query Functionality
- **NewRequest.tsx**: Completely rewritten to use simple query input
  - Removed complex sourcing form
  - Uses `/api/query/v1` endpoint
  - Stores results in sessionStorage
- **Candidates.tsx**: Completely rewritten to display Flask backend results
  - Reads results from sessionStorage
  - Displays vehicle results from Flask backend
  - Includes feedback functionality

### 4. ✅ Updated Other Pages
- **Concierge Services/Enroll**: Stub pages (not supported by Flask backend)
- **Build Orders**: Stub page (not supported by Flask backend)
- **Billing Portal**: Stub page (not supported by Flask backend)
- **Admin Dashboard**: Stub page (not supported by Flask backend)

### 5. ✅ API Client
- Created `src/lib/api.ts` with Flask backend API client
- Functions: `submitQuery()`, `submitQueryFeedback()`
- Types: `QueryRequest`, `QueryResponse`, `VehicleResult`

## Remaining Tasks

### 1. ⚠️ Remove Supabase Folder (Manual)
The `supabase/` folder needs to be manually deleted:
```
car_app-main/car_app-main/supabase/
  - functions/ (all Edge Functions)
  - migrations/ (all SQL migrations)
```

You can delete this folder manually, or run:
```bash
# Windows (PowerShell)
Remove-Item -Recurse -Force car_app-main\car_app-main\supabase

# macOS/Linux
rm -rf car_app-main/car_app-main/supabase
```

### 2. ⚠️ Environment Variables
Update `.env` or environment configuration:
- Remove: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`
- Add (optional): `VITE_API_BASE_URL` (defaults to `http://localhost:5000`)

### 3. ⚠️ Install Dependencies
After removing Supabase from package.json, run:
```bash
cd car_app-main/car_app-main
npm install
```

### 4. ⚠️ Update supabase.ts (Already Done)
The file `src/lib/supabase.ts` now redirects to the new API client. You can:
- Keep it temporarily for compatibility
- Or delete it and update any remaining imports

## How to Use

1. **Start Flask Backend** (from `car-full-repo/car-back-end`):
   ```bash
   python app.py
   ```
   Backend runs on `http://localhost:5000`

2. **Start Frontend** (from `car_app-main/car_app-main`):
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:5173` (Vite default)

3. **Use the App**:
   - Navigate to `/sourcing`
   - Enter a natural language query (e.g., "Looking for a manual corvette under 60k")
   - View results on `/sourcing/candidates`

## API Endpoints Used

### POST `/api/query/v1`
- **Request**: `{ "query": "natural language text" }`
- **Response**: `{ "success": true, "results": [...], "result_count": N, ... }`

### POST `/api/query/feedback`
- **Request**: `{ "query": "...", "extracted_fields": {...}, "sql_query": "...", "reason": "..." }`
- **Response**: `{ "success": true, "message": "..." }`

## Notes

- Authentication is disabled (mock user always logged in)
- Only vehicle search is functional
- Other features (concierge, build, billing, admin) show stub pages
- Results are stored in sessionStorage between pages
- All Supabase-specific code has been removed or stubbed out

