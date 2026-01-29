# RunPod Deployment Guide

This guide walks you through deploying the CAR Development Phase 1 backend to RunPod for GPU inference.

## Prerequisites

- RunPod account (sign up at https://www.runpod.io)
- GitHub repository with your code pushed
- HuggingFace account with your LoRA adapter uploaded
- Environment variables ready (see below)

## Option A: Build from GitHub (Recommended - No Docker Required)

This is the easiest method and doesn't require Docker installed locally.

### Steps:

1. **Push your code to GitHub**
   - Make sure `Dockerfile`, `.dockerignore`, and all backend code are committed and pushed
   - Your repository should be accessible (public or private with RunPod access)

2. **Login to RunPod**
   - Go to https://www.runpod.io
   - Sign up or login to your account

3. **Create a New Pod**
   - Navigate to "Pods" → "Deploy" or "Templates"
   - Look for "Custom Template" or "Deploy from Repository"
   - Connect your GitHub account if prompted

4. **Configure the Pod**
   - **Repository**: Select your GitHub repository (`CARDevelopment_Phase1`)
   - **Dockerfile Path**: `car-full-repo/car-back-end/Dockerfile`
   - **Context Path**: `car-full-repo/car-back-end`
   - **GPU Type**: Select a GPU with at least 8GB VRAM (e.g., RTX 3090, A40, A100)
   - **Container Disk**: At least 20GB (for model storage)

5. **Set Environment Variables**
   Add these in the RunPod pod configuration:
   ```
   HF_BASE_MODEL_ID=Qwen/Qwen2.5-3B
   LORA_ADAPTER_PATH=c4ritas/CARDevelopment_Phase1_Production_Model
   HF_TOKEN=your_huggingface_token_here
   FLASK_ENV=production
   PORT=5000
   CORS_ORIGINS=https://car-development-phase1.vercel.app
   ```

6. **Deploy**
   - Click "Deploy" or "Create Pod"
   - RunPod will automatically:
     - Pull your code from GitHub
     - Build the Docker image
     - Deploy to the GPU instance

7. **Get Your Backend URL**
   - Once deployed, RunPod will provide a public URL
   - It will look like: `https://xxxxx-5000.proxy.runpod.net`
   - Copy this URL

8. **Update Frontend**
   - Go to your Vercel project settings
   - Add/update environment variable:
     - `VITE_API_BASE_URL=https://xxxxx-5000.proxy.runpod.net`
   - Redeploy the frontend

## Option B: Build Locally and Push to Docker Hub

If you prefer to build locally (requires Docker Desktop):

1. **Build the image**
   ```bash
   cd car-full-repo/car-back-end
   docker build -t your-dockerhub-username/car-backend:latest .
   ```

2. **Push to Docker Hub**
   ```bash
   docker login
   docker push your-dockerhub-username/car-backend:latest
   ```

3. **Deploy on RunPod**
   - Create a new pod
   - Select "Docker Hub" as the image source
   - Enter: `your-dockerhub-username/car-backend:latest`
   - Configure environment variables (same as Option A)
   - Deploy

## Option C: Build Directly on RunPod

1. **Create a Pod with Terminal Access**
   - Select a GPU instance
   - Choose a base image (e.g., `runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel`)

2. **Clone and Build**
   ```bash
   git clone https://github.com/your-username/CARDevelopment_Phase1.git
   cd CARDevelopment_Phase1/car-full-repo/car-back-end
   docker build -t car-backend:latest .
   ```

3. **Run the Container**
   ```bash
   docker run -d \
     -p 5000:5000 \
     -e HF_BASE_MODEL_ID=Qwen/Qwen2.5-3B \
     -e LORA_ADAPTER_PATH=c4ritas/CARDevelopment_Phase1_Production_Model \
     -e HF_TOKEN=your_token \
     -e FLASK_ENV=production \
     -e PORT=5000 \
     -e CORS_ORIGINS=https://car-development-phase1.vercel.app \
     car-backend:latest
   ```

## Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `HF_BASE_MODEL_ID` | HuggingFace base model ID | Yes | `Qwen/Qwen2.5-3B` |
| `LORA_ADAPTER_PATH` | LoRA adapter path (HF Hub ID or local) | Yes | `c4ritas/CARDevelopment_Phase1_Production_Model` |
| `HF_TOKEN` | HuggingFace API token (for private models) | Yes | `hf_xxxxx` |
| `FLASK_ENV` | Flask environment | Yes | `production` |
| `PORT` | Port to run Flask on | Yes | `5000` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | Yes | `https://car-development-phase1.vercel.app` |

## Troubleshooting

### Build Fails with "blinker" Error
- The Dockerfile now includes a fix for this. If it still fails, the image will fall back to `--ignore-installed` flag.

### Model Loading Takes Too Long
- This is normal on first request. The model uses lazy loading (loads on first inference request).
- Subsequent requests will be faster.

### Out of Memory Errors
- Upgrade to a GPU with more VRAM (16GB+ recommended)
- The model uses float16 on GPU, which should fit in 8GB, but 16GB is safer

### Port Not Accessible
- Make sure port 5000 is exposed in RunPod pod settings
- Check that the pod has a public endpoint configured

## Next Steps

After deployment:
1. Test the backend endpoint: `https://your-pod-url.runpod.net/api/query/v1`
2. Update frontend `VITE_API_BASE_URL` in Vercel
3. Test end-to-end query flow
4. Monitor logs in RunPod dashboard
