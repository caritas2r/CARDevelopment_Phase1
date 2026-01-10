# Frontend Routes

## Available Routes

1. **Home Page**
   - URL: `http://localhost:8000/` or `http://localhost:8000/#/`
   - Displays: System status and backend connection information
   - Navigation: "Home" (primary button) and "View DB Schema" (secondary button)

2. **Database Schema Page**
   - URL: `http://localhost:8000/#/db-schema`
   - Displays: Database schema visualization with tables, columns, indexes, and foreign keys
   - Navigation: "Back to Home" (secondary button) and "DB Schema" (primary button)

## Navigation

Both pages have navigation buttons in the header:
- **Primary button**: Blue background, white text (indicates current page)
- **Secondary button**: Transparent with blue border, blue text (for navigation)

## Troubleshooting

### If you see the same content on both pages:

1. **Hard refresh the browser**:
   - Windows/Linux: `Ctrl + Shift + R` or `Ctrl + F5`
   - Mac: `Cmd + Shift + R`

2. **Clear browser cache**:
   - Open browser DevTools (F12)
   - Right-click the refresh button
   - Select "Empty Cache and Hard Reload"

3. **Check browser console** (F12):
   - Look for `[Router]` log messages
   - Verify both render functions are available
   - Check for any JavaScript errors

4. **Verify the URL hash**:
   - Home page should show: `localhost:8000/#/` or `localhost:8000/`
   - Schema page should show: `localhost:8000/#/db-schema`

### If buttons are not visible:

1. Check that both CSS files are loading:
   - `src/containers/home-page/style.css`
   - `src/containers/db-schema-page/style.css`

2. Verify in browser DevTools (F12) → Network tab that both CSS files load successfully

3. Check browser console for CSS errors


