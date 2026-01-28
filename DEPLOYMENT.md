# Deployment Guide

This guide covers deployment of the CAR Development Phase 1 application.

## Architecture

The application consists of two separate components:

1. **Frontend**: React/TypeScript application (deploy to Vercel)
2. **Backend**: Python Flask API (deploy to Railway, Render, Heroku, or AWS)

## Frontend Deployment (Vercel)

### Prerequisites

- Vercel account
- Repository connected to Vercel
- Backend API URL (for production)

### Steps

1. **Connect Repository**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New Project"
   - Import your Git repository

2. **Configure Project Settings**
   - **Root Directory**: `car_app-main/car_app-main` (or update `vercel.json` if restructured)
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

3. **Environment Variables**
   - Add `VITE_API_BASE_URL`: Your production backend API URL
     - Example: `https://your-backend-api.railway.app` or `https://api.yourdomain.com`

4. **Deploy**
   - Click "Deploy"
   - Vercel will automatically build and deploy your frontend

### Vercel Configuration

The `vercel.json` file in the root directory configures:
- Build and install commands
- SPA routing (rewrites all routes to `index.html`)
- Environment variables

### Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

## Backend Deployment

The Flask backend should be deployed to a platform that supports Python applications.

### Option 1: Railway

1. **Create Account**: Sign up at [Railway](https://railway.app)

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your repository

3. **Configure Service**
   - **Root Directory**: `car-full-repo/car-back-end`
   - **Start Command**: `python app.py`
   - **Python Version**: 3.10+

4. **Environment Variables**
   - `STRIPE_API_KEY`: Your Stripe API key
   - `PORT`: Railway will set this automatically
   - `HF_BASE_MODEL_ID`: (Optional) For ML inference
   - `LORA_ADAPTER_PATH`: (Optional) For ML inference

5. **Deploy**
   - Railway will automatically detect Python and install dependencies
   - The service will start automatically

6. **Get API URL**
   - Railway provides a URL like `https://your-app.railway.app`
   - Use this URL as `VITE_API_BASE_URL` in Vercel

### Option 2: Render

1. **Create Account**: Sign up at [Render](https://render.com)

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your repository

3. **Configure Service**
   - **Name**: `car-backend` (or your choice)
   - **Root Directory**: `car-full-repo/car-back-end`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

4. **Environment Variables**
   - Add the same variables as Railway (see above)

5. **Deploy**
   - Render will build and deploy automatically

### Option 3: Heroku

1. **Install Heroku CLI**: [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

2. **Create App**
   ```bash
   heroku create your-app-name
   ```

3. **Set Buildpack**
   ```bash
   heroku buildpacks:set heroku/python
   ```

4. **Configure Procfile**
   Create `car-full-repo/car-back-end/Procfile`:
   ```
   web: python app.py
   ```

5. **Set Environment Variables**
   ```bash
   heroku config:set STRIPE_API_KEY=your_key
   heroku config:set PORT=$PORT
   ```

6. **Deploy**
   ```bash
   cd car-full-repo/car-back-end
   git subtree push --prefix car-full-repo/car-back-end heroku main
   ```

### Option 4: AWS (Elastic Beanstalk)

1. **Install EB CLI**: [AWS Elastic Beanstalk CLI](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html)

2. **Initialize EB**
   ```bash
   cd car-full-repo/car-back-end
   eb init -p python-3.10
   ```

3. **Create Environment**
   ```bash
   eb create car-backend-env
   ```

4. **Set Environment Variables**
   ```bash
   eb setenv STRIPE_API_KEY=your_key
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

## Database

The backend uses SQLite for local development. For production, consider:

- **PostgreSQL** (recommended for production)
- **MySQL**
- **SQLite** (only for small-scale deployments)

### Database Migration

If migrating to PostgreSQL:

1. Update `car-full-repo/car-back-end/services/database_connection_service.py` to use PostgreSQL
2. Update connection string in environment variables
3. Run database migrations (if using Alembic or similar)

## Environment Variables Summary

### Frontend (Vercel)
- `VITE_API_BASE_URL`: Backend API URL (required)

### Backend (Railway/Render/Heroku/AWS)
- `STRIPE_API_KEY`: Stripe API key for payments (required)
- `PORT`: Server port (usually set by platform)
- `HF_BASE_MODEL_ID`: HuggingFace model ID (optional, for ML inference)
- `LORA_ADAPTER_PATH`: Path to LoRA adapter (optional, for ML inference)
- `HF_HOME`: HuggingFace cache directory (optional)

## Post-Deployment

### 1. Update Frontend API URL

After backend deployment, update the frontend environment variable:
- Go to Vercel Dashboard → Your Project → Settings → Environment Variables
- Update `VITE_API_BASE_URL` with your backend URL
- Redeploy frontend

### 2. Test Endpoints

Test the deployed backend:
```bash
curl https://your-backend-url.railway.app/api/health
```

### 3. CORS Configuration

Ensure the backend allows requests from your frontend domain:
- Check `car-full-repo/car-back-end/app.py` for CORS configuration
- Add your Vercel domain to allowed origins if needed

### 4. Database Setup

The backend will automatically create the database schema on first startup. For production:
- Ensure the database file/directory is writable
- Consider using a managed database service
- Set up database backups

## Monitoring

### Frontend (Vercel)
- Vercel provides built-in analytics and monitoring
- Check deployment logs in Vercel Dashboard

### Backend
- **Railway**: Built-in logs and metrics
- **Render**: Logs available in dashboard
- **Heroku**: `heroku logs --tail`
- **AWS**: CloudWatch logs

## Troubleshooting

### Frontend Issues

**Build Fails**
- Check Node.js version (should be 18+)
- Verify all dependencies are in `package.json`
- Check build logs in Vercel Dashboard

**API Calls Fail**
- Verify `VITE_API_BASE_URL` is set correctly
- Check CORS configuration in backend
- Verify backend is running and accessible

### Backend Issues

**Application Won't Start**
- Check Python version (should be 3.10+)
- Verify all dependencies in `requirements.txt`
- Check environment variables are set
- Review application logs

**Database Errors**
- Ensure database file/directory is writable
- Check database connection string
- Verify database schema is created

## Security Considerations

1. **Environment Variables**: Never commit sensitive keys to Git
2. **CORS**: Restrict CORS to your frontend domain only
3. **API Keys**: Use environment variables, never hardcode
4. **Database**: Use strong passwords and secure connections
5. **HTTPS**: Always use HTTPS in production

## Cost Estimates

### Vercel (Frontend)
- **Hobby Plan**: Free (suitable for development)
- **Pro Plan**: $20/month (for production)

### Railway (Backend)
- **Hobby Plan**: $5/month (includes $5 credit)
- **Pro Plan**: Pay-as-you-go

### Render (Backend)
- **Free Tier**: Available (with limitations)
- **Starter Plan**: $7/month

### Heroku (Backend)
- **Eco Dyno**: $5/month
- **Basic Dyno**: $7/month

## Support

For issues or questions:
- Check application logs
- Review deployment platform documentation
- See project README files for setup instructions
