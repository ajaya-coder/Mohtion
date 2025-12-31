FROM python:3.12-slim

WORKDIR /app

# Install git (needed for GitPython)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy dependency files first
COPY pyproject.toml .
COPY README.md .

# Copy application code BEFORE installing
COPY mohtion/ mohtion/

# Install dependencies (package source now available)
RUN pip install --no-cache-dir -e .

# Expose port for documentation
EXPOSE 8000

# Default command (overridden by railway.toml)
CMD ["uvicorn", "mohtion.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
