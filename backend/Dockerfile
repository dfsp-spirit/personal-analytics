FROM python:3.11-slim

WORKDIR /app

# Install UV for fast package management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./

# Create virtual environment
RUN uv venv

# Install dependencies
RUN uv pip install -e .

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "personal_analytics_backend.api:app", "--host", "0.0.0.0", "--port", "8000"]