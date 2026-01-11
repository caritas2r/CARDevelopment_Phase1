# Migration Complete: Supabase → Flask Backend

## Quick Start

1. **Install dependencies** (removed Supabase):
   ```bash
   npm install
   ```

2. **Start Flask backend** (from `car-full-repo/car-back-end`):
   ```bash
   python app.py
   ```

3. **Start frontend**:
   ```bash
   npm run dev
   ```

4. **Use the app**:
   - Navigate to `/sourcing`
   - Enter a query like "Looking for a manual corvette under 60k"
   - View results

## What Changed

- ✅ Removed Supabase dependencies
- ✅ Created Flask API client (`src/lib/api.ts`)
- ✅ Simplified authentication (mock user)
- ✅ Replaced complex sourcing form with simple query input
- ✅ Updated results page to display Flask backend results
- ✅ Stubbed out unsupported features (concierge, build, billing, admin)

## Manual Steps Required

1. **Delete supabase folder**:
   ```bash
   # Windows PowerShell
   Remove-Item -Recurse -Force supabase
   
   # macOS/Linux
   rm -rf supabase
   ```

2. **Update environment variables** (if using .env):
   - Remove: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`
   - Optional: Add `VITE_API_BASE_URL` (defaults to `http://localhost:5000`)

## API Configuration

The Flask backend API base URL defaults to `http://localhost:5000`. To change it, set the environment variable:

```bash
VITE_API_BASE_URL=http://localhost:5000
```

See `MIGRATION_SUMMARY.md` for detailed information about the migration.

