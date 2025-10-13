# personal-analytics

A web-based, mobile-friendly, experimental personal analytics app to understand life patterns and mess with time-series analysis and AI-based predictions. The idea is that you quickly fill out the same few questions every day over longer periods of time.

This is not intended for self optimization, it's more about understanding what influences your wellbeing, and how. But you can adapt the data you track to your needs, of course.

Whatever you use it for, you can use this to understand trends over time, to look into correlations between the dimensions you track, or to see whether certain events can serve to predict others on consecutive days.

In any case, be careful when drawing conclusions. Don't take it too seriously unless you have put a lot of thought into data quality, filtering outliers, identifying and tracking possible confounding variables, interpolating missing values, etc. Basically follow good study design and data science practices, which will require domain knowledge.


## Development state

Very early alpha, definitely not ready for production.

## Frontend

### Frontend Development Setup (see below for Docker alternative)

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

### Backend Development Setup (see below for Docker alternative)

First clone the repo, if you do not have it yet:

```sh
git clone https://github.com/dfsp-spirit/personal-analytics
cd personal-analytics/
```

Create the file `backend/.env` with database credentials. You can copy the template file and edit it:

```sh
cp backend/.env.example backend/.env
vim backend/.env # Adapt it!
```


Then setup the postgresql database:

```sh
sudo apt install postgresql
cd backend/
./setup_db.sh   # will use settings from <repo_root>/backend/.env
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


## Alternative: Use Docker to run both the Frontend and the Backend in containers

Make sure you have `docker` and docker compose, and that you are allowed to use it. If you're not in the `docker` system group, you will have to use `sudo` to run docker.

Note that [docker-compose.yml](./docker-compose.yml) maps the postgresql port of the container to the default postgresql port on your host system, so you can easily access the database. This will of course fail if that port is already in use, e.g. by a postgresql server running on your host system. In that case, either change the port mapping in the Docker compose file, or change the port of your local postgresql server.

First create the file `<repo_root>/.env` with database credentials. You can copy the template file and edit it:

```sh
cp backend/.env.example .env
vim .env # Adapt it!
```


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


## Deployment options

### Bare metal

If you want to deploy the backend under Linux bare metal, you should create a system service for it, along with a dedicated user.

Create app dir, user, and install backend there:

```sh
# Create dedicated user
sudo adduser --system --group --home /opt/personal-analytics personal-analytics

# Create app directory
sudo mkdir -p /opt/personal-analytics/backend
sudo chown personal-analytics:personal-analytics /opt/personal-analytics

# Switch to service user and install app in the service directory
sudo su - personal-analytics
cd /opt/personal-analytics

# Now your part: install the app as described above, with production settings, proper passwords in .env file, etc.

exit # back to your user once you are done.
```

Setup system service. E.g., for Ubuntu, copy the template service file from this repo, adapt it to your system and service user, then start it with systemctl. E.g.,


```sh
sudo cp backend/deployment/persona-analytics.service.template /etc/systemd/system/personal-analytics.service
sudo vim /etc/systemd/system/personal-analytics.service  # Adapt user, security, path to the software and venv you created during installation, etc. Required.
```

Now you can use standard systemctl commands to manage the service, e.g.,

```sh
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable to start on boot
sudo systemctl enable personal-analytics.service

# Start the service now, stop it now, restart it
sudo systemctl start personal-analytics.service
sudo systemctl stop personal-analytics.service
sudo systemctl restart personal-analytics.service

# Check status
sudo systemctl status personal-analytics.service

# View logs
sudo journalctl -u personal-analytics.service -f
```
