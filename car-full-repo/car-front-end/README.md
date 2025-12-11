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

3. Start a local server:

   **Using Python:**
   ```bash
   cd car-front-end
   python -m http.server 8000
   ```
   Then open `http://localhost:8000` in your browser

   **Using Node.js (http-server):**
   ```bash
   npx http-server car-front-end -p 8000
   ```

## Project Structure

```
car-front-end/
├── index.html           # Main HTML file
├── app.js              # App entry point (routing)
├── package.json        # Dependencies
└── src/
    └── containers/
        └── home-page/
            ├── index.js    # Home page logic
            └── style.css   # Home page styles (Carbon Design System)
```

## Design System

This application uses IBM Carbon Design System v11 for consistent, accessible UI components and design patterns.

## Configuration

If your backend runs on a different URL/port, update the `API_BASE_URL` in `src/containers/home-page/index.js`:

```javascript
const API_BASE_URL = 'http://your-backend-url:port';
```