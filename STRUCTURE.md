# Repository Structure

This document provides a clear overview of the repository structure and organization.

## Directory Structure

```
CARDevelopment_Phase1/
│
├── README.md                    # Main project README
├── DEPLOYMENT.md                # Deployment guide
├── STRUCTURE.md                 # This file
├── .gitignore                   # Root gitignore
├── vercel.json                  # Vercel deployment configuration
│
├── car_app-main/                # Frontend application directory
│   └── car_app-main/            # React/TypeScript frontend (Vite)
│       ├── src/                 # Source code
│       │   ├── components/      # React components
│       │   ├── pages/           # Page components
│       │   ├── hooks/           # Custom hooks
│       │   ├── lib/             # API clients and utilities
│       │   └── store/           # State management
│       ├── public/              # Static assets
│       ├── package.json         # Frontend dependencies
│       ├── vite.config.ts       # Vite configuration
│       └── README.md            # Frontend documentation
│
└── car-full-repo/               # Backend and legacy code
    ├── car-back-end/            # Flask API backend
    │   ├── app.py               # Application entry point
    │   ├── services/            # Microservices
    │   ├── schemas/             # Vehicle Selection V1 schema
    │   ├── training/            # ML training pipeline
    │   ├── utils/               # Utility scripts
    │   ├── data/                # Database files
    │   ├── docs/                # Backend documentation
    │   └── README.md            # Backend documentation
    │
    ├── car-front-end/           # Legacy frontend (deprecated)
    │   └── README.md            # Notes about deprecation
    │
    ├── car-models/              # ML model files (gitignored)
    ├── hf_cache/                # HuggingFace cache (gitignored)
    ├── data/                    # Training data
    ├── env_var                  # Environment variables (gitignored)
    └── README.md                # Legacy documentation
```

## Key Components

### Frontend (`car_app-main/car_app-main/`)

- **Technology**: React 18+ with TypeScript, Vite
- **Purpose**: User interface for vehicle selection
- **Deployment**: Vercel
- **Documentation**: `car_app-main/car_app-main/README.md`

### Backend (`car-full-repo/car-back-end/`)

- **Technology**: Python 3.10+, Flask 3.0+
- **Purpose**: REST API for vehicle queries and processing
- **Deployment**: Railway, Render, Heroku, or AWS
- **Documentation**: `car-full-repo/car-back-end/README.md`

### Legacy Frontend (`car-full-repo/car-front-end/`)

- **Status**: Deprecated, not in use
- **Technology**: Vanilla JavaScript
- **Purpose**: Kept for reference only
- **Documentation**: `car-full-repo/car-front-end/README.md`

## Important Notes

### Directory Naming

The frontend is currently located at `car_app-main/car_app-main/` due to historical reasons. For cleaner organization, consider:

1. **Option A**: Keep current structure (works as-is)
2. **Option B**: Move to `frontend/` at root level
   - Update `vercel.json` paths
   - Update `start-dev.bat` paths
   - Update documentation

### Git Ignored Files

The following are gitignored and should not be committed:

- `node_modules/` - Frontend dependencies
- `dist/` - Frontend build output
- `__pycache__/` - Python cache files
- `*.db`, `*.sqlite` - Database files
- `car-models/` - ML model files
- `hf_cache/` - HuggingFace cache
- `env_var` - Environment variables
- `.env` files - Environment configuration

### Environment Variables

**Frontend** (Vercel):
- `VITE_API_BASE_URL` - Backend API URL

**Backend** (Railway/Render/etc.):
- `STRIPE_API_KEY` - Stripe payment API key
- `PORT` - Server port (usually auto-set)
- `HF_BASE_MODEL_ID` - HuggingFace model ID (optional)
- `LORA_ADAPTER_PATH` - LoRA adapter path (optional)

## Development Workflow

1. **Local Development**:
   - Use `start-dev.bat` to start both frontend and backend
   - Or start manually: backend on port 5000/5001, frontend on port 5173/5174

2. **Testing**:
   - Frontend: `npm run dev` in `car_app-main/car_app-main/`
   - Backend: `python app.py` in `car-full-repo/car-back-end/`

3. **Deployment**:
   - Frontend: Deploy to Vercel (see `DEPLOYMENT.md`)
   - Backend: Deploy to Railway/Render/Heroku/AWS (see `DEPLOYMENT.md`)

## Documentation Files

- **README.md** - Main project overview and quick start
- **DEPLOYMENT.md** - Detailed deployment instructions
- **STRUCTURE.md** - This file (repository structure)
- **car_app-main/car_app-main/README.md** - Frontend documentation
- **car-full-repo/car-back-end/README.md** - Backend documentation
- **car-full-repo/car-back-end/schemas/README.md** - Schema documentation
- **car-full-repo/car-back-end/utils/DB_BOOTSTRAP_README.md** - Database schema docs

## Migration Notes

The repository has been migrated from Supabase to Flask backend. Migration documents have been removed as they are no longer needed. The current architecture uses:

- React frontend → Flask backend API
- No Supabase dependencies
- Simplified authentication (mock user for development)

## Future Improvements

1. **Directory Structure**: Consider flattening `car_app-main/car_app-main/` to `frontend/`
2. **Database**: Consider migrating from SQLite to PostgreSQL for production
3. **Authentication**: Implement proper authentication system
4. **Testing**: Add unit and integration tests
5. **CI/CD**: Set up automated testing and deployment pipelines
