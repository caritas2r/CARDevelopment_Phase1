# CAR Development - Phase 1

A full-stack vehicle selection application with a React/TypeScript frontend and Python Flask backend.

## Project Structure

```
CARDevelopment_Phase1/
├── frontend/                          # React/TypeScript frontend (Vite)
│   ├── src/                           # Source code
│   │   ├── components/                # React components
│   │   ├── pages/                     # Page components
│   │   ├── hooks/                     # Custom React hooks
│   │   ├── lib/                       # API clients and utilities
│   │   └── store/                     # State management
│   ├── public/                        # Static assets
│   ├── package.json                   # Frontend dependencies
│   └── vite.config.ts                 # Vite configuration
│
├── car-full-repo/                     # Backend and legacy code
│   ├── car-back-end/                  # Flask API backend
│   │   ├── app.py                     # Application entry point
│   │   ├── services/                  # Microservices
│   │   ├── schemas/                   # Vehicle Selection V1 schema
│   │   ├── training/                  # ML training pipeline
│   │   ├── utils/                     # Utility scripts
│   │   └── data/                      # Database files
│   │
│   ├── car-front-end/                 # Legacy frontend (deprecated)
│   │   └── [vanilla JS frontend - not in use]
│   │
│   └── car-models/                    # ML model files (gitignored)
│
└── start-dev.bat                      # Development launcher script
```

## Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- **Flask backend** dependencies installed

### Development Setup

1. **Install frontend dependencies:**
   ```bash
   cd car_app-main/car_app-main
   npm install
   ```

2. **Set up backend (from `car-full-repo`):**
   ```bash
   cd car-full-repo/car-back-end
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Start development servers:**

   **Option A: Use launcher script (Windows)**
   ```bash
   start-dev.bat
   ```

   **Option B: Manual start**
   ```bash
   # Terminal 1 - Backend
   cd car-full-repo/car-back-end
   python app.py
   
   # Terminal 2 - Frontend
   cd car_app-main/car_app-main
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000

## Deployment

### Frontend (Vercel)

The frontend is configured for Vercel deployment. See `vercel.json` for configuration.

**Deploy to Vercel:**
1. Connect your repository to Vercel
2. Set root directory to `car_app-main/car_app-main` (or `frontend/` if restructured)
3. Set build command: `npm run build`
4. Set output directory: `dist`
5. Add environment variable: `VITE_API_BASE_URL` (your backend API URL)

### Backend

The Flask backend should be deployed separately (not to Vercel):
- **Recommended platforms:** Railway, Render, Heroku, or AWS
- **Environment variables needed:**
  - `STRIPE_API_KEY` (for payment processing)
  - `HF_BASE_MODEL_ID` (for ML inference, optional)
  - `LORA_ADAPTER_PATH` (for ML inference, optional)

## Technology Stack

### Frontend
- **React** 18.3+ with TypeScript
- **Vite** for build tooling
- **React Router** for routing
- **TanStack Query** for data fetching
- **React Hook Form** with Zod validation
- **Tailwind CSS** for styling
- **Lucide React** for icons

### Backend
- **Python** 3.10+
- **Flask** 3.0+ with Flask-CORS
- **SQLite** for local database
- **JSON Schema** validation
- **Stripe** for payment processing

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/db/health` - Database health check
- `GET /api/schema/v1` - Get Vehicle Selection V1 JSON schema
- `POST /api/query/v1` - Process natural language vehicle queries
  - Request: `{ "query": "natural language text" }`
  - Response: `{ "success": true, "results": [...], "result_count": N }`
- `POST /api/query/feedback` - Submit feedback for queries
- `POST /api/payment/process` - Process payment via Stripe

## Features

- **Natural Language Vehicle Search**: Query vehicles using natural language
- **Vehicle Results Display**: View detailed vehicle information
- **Payment Integration**: Stripe payment processing for premium features
- **Query Feedback**: Submit feedback for query results
- **Responsive Design**: Mobile-friendly interface

## Documentation

- **Repository Structure**: See `STRUCTURE.md` for detailed directory structure
- **Deployment Guide**: See `DEPLOYMENT.md` for deployment instructions
- **Backend API**: See `car-full-repo/car-back-end/README.md`
- **Frontend**: See `car_app-main/car_app-main/README.md`
- **Schema Documentation**: See `car-full-repo/car-back-end/schemas/README.md`
- **Database Schema**: See `car-full-repo/car-back-end/utils/DB_BOOTSTRAP_README.md`

## Notes

- The legacy frontend in `car-full-repo/car-front-end/` is deprecated and not in use
- ML model files in `car-full-repo/car-models/` are gitignored
- Database files (`*.db`) are gitignored
- Environment variables should be set via `.env` files or deployment platform settings
