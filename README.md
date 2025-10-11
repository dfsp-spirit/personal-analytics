# personal-analytics
Highly experimental personal analytics app to understand life patterns and mess with time-series analysis and AI-based predictions.

Don't take it too seriously.




## Frontend

### Frontend Development setup

First clone the repo:

```sh
git clone https://github.com/dfsp-spirit/personal-analytics
cd personal-analytics/
```


Just open the file [frontend/index.html](./frontend/index.html) in your favourite text editor or IDE, e.g.,

```sh
cd frontend/
code .
```

To run it:

```sh
# we are still in <repo>/frontend/
python -m http.server 3000
```


## Backend

Make sure you have `uv`.

### Development setup

First clone the repo, if you do not have it yet:

```sh
git clone https://github.com/dfsp-spirit/personal-analytics
cd personal-analytics/
```

Then install in dev mode:

```sh
cd backend
uv venv   # Create virtual env and install deps with uv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install package in editable mode
uv pip install -e .

# Or install with dev dependencies
uv pip install -e ".[dev]"
```

To run it once its installed:

```sh
# still in <repo>/backend/
uvicorn personal_analytics_backend.api:app --reload --host 0.0.0.0 --port 8000
```


## Alternative: Docker for both Frontend and Backend in containers

```sh
# Start everything
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop everything
docker-compose down

# Stop and remove volumes (full cleanup)
docker-compose down -v
```

Access your services:

* Frontend: http://localhost:3000
* Backend API: http://localhost:8000
* API Docs: http://localhost:8000/docs
* PostgreSQL: localhost:5432