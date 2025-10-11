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

To run, just open `index.html` in your browser:

```sh
firefox ./index.html
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