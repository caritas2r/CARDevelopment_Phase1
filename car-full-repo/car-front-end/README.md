# Car Frontend

A lightweight frontend application built with IBM Carbon Design System v11.

## Features

- IBM Carbon Design System v11 styling
- Vanilla JavaScript (ES6 modules)
- Container-based architecture
- Responsive design

## Setup

1. Install dependencies (optional - for Carbon styles):
```bash
npm install
```

Note: Currently using Carbon design tokens via CSS. For full Carbon component library, you would need to install `@carbon/styles`.

2. Make sure the Flask backend is running on `http://localhost:5000`

3. Start a local development server (recommended - no cache issues):

   **Using Node.js (recommended for development):**
   ```bash
   cd car-front-end
   npm run dev
   # or
   node dev-server.js
   ```
   This server sets no-cache headers automatically, so you won't need to clear cache!

   **Using Python:**
   ```bash
   cd car-front-end
   python dev-server.py
   ```
   This also sets no-cache headers automatically.

   **Using standard Python http.server (may cache files):**
   ```bash
   cd car-front-end
   python -m http.server 8000
   ```
   ⚠️ Note: This may cache files. Use `dev-server.py` instead for development.

   **Using Node.js http-server (may cache files):**
   ```bash
   npx http-server car-front-end -p 8000
   ```
   ⚠️ Note: This may cache files. Use `dev-server.js` instead for development.

4. Open `http://localhost:8000` in your browser

## Development Tips

### Avoiding Cache Issues

**Option 1: Use the development servers (recommended)**
- Use `npm run dev` or `python dev-server.py`
- These automatically set no-cache headers

**Option 2: Browser DevTools**
- Open DevTools (F12)
- Go to Network tab
- Check "Disable cache" checkbox
- Keep DevTools open while developing

**Option 3: Hard Refresh**
- Windows/Linux: `Ctrl + Shift + R` or `Ctrl + F5`
- Mac: `Cmd + Shift + R`

## Project Structure

```
car-front-end/
├── index.html           # Main HTML file
├── app.js              # App entry point (routing)
├── package.json        # Dependencies
├── dev-server.js       # Node.js dev server (no cache)
├── dev-server.py       # Python dev server (no cache)
└── src/
    └── containers/
        └── home-page/
            ├── index.js    # Home page logic
            └── style.css   # Home page styles (Carbon Design System)
```

## Design System

This application uses IBM Carbon Design System v11 for consistent, accessible UI components and design patterns.

## Configuration

If your backend runs on a different URL/port, update the `API_BASE_URL` in each container file:
- `src/containers/home-page/index.js`
- `src/containers/query-page/index.js`
- `src/containers/db-schema-page/index.js`

```javascript
const API_BASE_URL = 'http://your-backend-url:port';
```
