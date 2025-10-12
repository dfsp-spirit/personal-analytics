# personal-analytics

A web-based, mobile-friendly, experimental personal analytics app to understand life patterns and mess with time-series analysis and AI-based predictions. The idea is that you quickly fill out the same few questions every day over longer periods of time.

This is not intended for self optimization, it's more about understanding what influences your wellbeing, and how. But you can adapt the data you track to your needs, of course.

Whatever you use it for, you can use this to understand trends over time, to look into correlations between the dimensions you track, or to see whether certain events can serve to predict others on consecutive days.

In any case, be careful when drawing conclusions. Don't take it too seriously unless you have put a lot of thought into data quality, filtering outliers, identifying and tracking possible confounding variables, interpolating missing values, etc. Basically follow good study design and data science practices, which will require domain knowledge.


## Development state

Very early alpha, definitely not ready for production.

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