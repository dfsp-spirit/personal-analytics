FROM python:3.11-slim

WORKDIR /app

# Install UV for fast package management
RUN pip install uv

COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN uv run pip install --system -e .



EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1


# Use uv run to execute within the virtual environment
CMD ["uvicorn", "personal_analytics_backend.api:app", "--host", "0.0.0.0", "--port", "8000"]