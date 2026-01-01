# ============================================
# Stage 1: Build Next.js Landing Page
# ============================================
FROM node:20-slim AS frontend-builder

WORKDIR /frontend

# Copy package files
COPY landing_page/package*.json ./

# Install dependencies (includes devDependencies for TypeScript)
RUN npm ci

# Copy landing page source
COPY landing_page/ ./

# Build static export
RUN npm run build

# Debug: Verify Next.js created the out directory
RUN echo "=== Checking Next.js build output ===" && \
    ls -la /frontend/ && \
    echo "=== Contents of out directory ===" && \
    ls -la /frontend/out/ || echo "ERROR: out directory not found"

# ============================================
# Stage 2: Python Backend + Static Files
# ============================================
FROM python:3.12-slim

WORKDIR /app

# Install git (required for GitPython)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy dependency files first
COPY pyproject.toml .
COPY README.md .

# Copy application code BEFORE installing
COPY mohtion/ mohtion/

# Install dependencies (package source now available)
RUN pip install --no-cache-dir -e .

# Copy static files from frontend build
COPY --from=frontend-builder /frontend/out /app/static

# Debug: Verify static files were copied
RUN echo "=== Verifying static files copied ===" && \
    ls -la /app/ && \
    echo "=== Contents of static directory ===" && \
    ls -la /app/static/ || echo "ERROR: static directory not found"

# Expose port for documentation
EXPOSE 8000

# Default command (overridden by railway.toml)
CMD ["uvicorn", "mohtion.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
