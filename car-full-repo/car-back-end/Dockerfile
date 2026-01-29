# Dockerfile for RunPod GPU deployment
FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version to handle package conflicts better
RUN pip install --upgrade pip

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Use --force-reinstall for packages that may conflict with distutils-installed versions
RUN pip install --no-cache-dir --force-reinstall -r requirements.txt || \
    pip install --no-cache-dir --ignore-installed -r requirements.txt

# Copy application code
COPY . .

# Expose Flask port
EXPOSE 5000

# Set environment variables (can be overridden in RunPod)
ENV FLASK_ENV=production
ENV PORT=5000

# Start command
CMD ["python", "app.py"]
