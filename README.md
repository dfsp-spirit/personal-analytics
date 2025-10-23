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
python -m http.server 3000  # serve frontend on http://localhost:3000
```

The only configuration you may want to do is to adapt the backend API url. It can be found in [frontend/settings.js](./frontend/settings.js), find the line `const API_BASE_URL = 'http://localhost:8000'`; The default value should work for local development and points to the default value used in the backend.

Note that in our development Docker image, the backend does not run on `localhost`, but on `backend`. Therefore, the Dockerfile copies `frontend/settings.docker.js` over `frontend/settings.js`. In that file, the default is `const API_BASE_URL = 'http://backend:8000'`.

Note that if you deploy to your production bare metal server or your own production Docker image, you will (hopefully) use HTTPS and an ngingx reverse proxy instead of exposing uvicorn directly to the internet. That means your API_BASE_URL would be something like `https://your-production-domain/path_to_backend`, i.e., it will use the standard HTTPS port (443). So you will have uvicorn running on 127.0.0.1:8000 (not 0.0.0.0:8000), and thus users can only access it via nginx, which runs HTTPS on 443.


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
sudo ./setup_db.sh   # will use settings from <repo_root>/backend/.env, requires sudo
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
uv run uvicorn personal_analytics_backend.api:app --reload --host 127.0.0.1 --port 8000
```

You can now access your services:

* Frontend: http://localhost:3000
* Backend API: http://localhost:8000
* PostgreSQL: postgresql://localhost:5432 or using peer authentication as system user `postgresql` (if allowed in your system's `pg_hba.conf`)

## Alternative: Use Docker to run both the Frontend and the Backend in containers (development mode)

**IMPORTANT**: *The Docker setup provided in this repo is meant for development. Do not use it for production. It does many things that are not secure, e.g., no HTTPS, expose uvicorn directly, etc.*

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

The ports get mapped in the [docker-compose.yml](./docker-compose.yml) file, so you can access all services directly from the host computer:

* Frontend: http://localhost
* Backend API: http://localhost:8000
* PostgreSQL: postgresql://localhost:5432


## Documentation

* How to configure the form to my needs, i.e., change the questions in the questionaire?
    - In the frontend:
        * the form is generated from the definition in variable `FORM_CONFIG` in file [frontend/form-config.js](./frontend/form-config.js). Look at the examples and add or replace the fields as you see fit.
    - In the backend:
  -     * each key in the FORM_CONFIG of the frontend goes to a column in the database. You need to adapt the data model in the file [backend/src/personal_analytics_backend/models.py](./backend/src/personal_analytics_backend/models.py) to suit the changes you made in the frontend. Have a look at the existing entries, it's easy.
  -     * in the file [backend/src/personal_analytics_backend/api.py](./backend/src/personal_analytics_backend/api.py), you need to adapt the functions `export_all_data_csv()` so that your new fields are handled on data export to CSV files. The function `export_all_data_json()` in the same file should not need changes typically, but double-check it.
* I need a new custom input component that is not available yet, i.e., my new entry to the `FORM_CONFIG` must have a type other than the existing ones (`slider`, `radio`, `select`, ...).
    - In that case you will need to make changes to several functions in the frontend:
        * Add a new field to your `FORM_CONFIG` in [form-config.js](./frontend/form-config.js) that uses your new type, so that you can see whether it works.
        * In [form-generator.js](./frontend/form-generator.js), add a new function `function generateYourNewCustomComponent(fieldName, config) {...}`. It should generate the HTML for the component, see existing examples like `generateNumberSlider()`.
        * in [form-generator.js](./frontend/form-generator.js), update the main switch statement in the function `generateFormField()`: In the `switch(config.type) {...\}` statement, add a new case for the new form type of your custom component.
        * In [form-config.js](./frontend/form-config.js), update the `loadDataIntoForm()` function to handle fields with your new component type. The function muss take the data saved to the database and use it to fill the component, so that the component can correctly display existing entries. Take a look at the other examples, it's easy.
        * In [styles.css](./frontend/styles.css), add the new style definitions for your component
    - As descibed above, you will also need to adapt the database model to make sure the new field that will be send to the backend is recognized and saved properly.
        * Add a new field to your FORM_CONFIG in form-config.js that uses your new type, so that you can see whether it works.
        * In [form-generator.js](./frontend/form-generator.js), add a new function `function generateYourNewCustomComponent(fieldName, config) {...}`. It should generate the HTML for the component, see existing examples like `generateNumberSlider()`.
        * in [form-generator.js](./frontend/form-generator.js), update the main switch statement in the function `generateFormField()`: In the `switch(config.type) {...\}` statement, add a new case for the new form type of your custom component.
        * In form-config.js, update the `loadDataIntoForm()` function to handle fields with your new component type. The function muss take the data saved to the database and use it to fill the component, so that the component can correctly display existing entries. Take a look at the other examples, it's easy.
        * In [styles.css](./frontend/styles.css), add the new style definitions for your component
    - As descibed in the first question above, you will also need to adapt the database model to make sure the new field that will be send to the backend is recognized and saved properly, and adapt the data export functions.

### Troubleshooting

* When opening the web app in the browser, I see no data in the form and I cannot submit. In web developer tools console, I see a network error with reason 'CORS request not HTTP'. What does this mean?
    - There are different options why this happens, but in general some resource you load in your frontend code is not loaded from HTTP/HTTPS scheme (a link starting with `http://` or `https://`), but something different, e.g., from `file:///` or something implicitely interpreted as such. This can happen if you give, in the `frontend/settings.js` file, something like `const API_BASE_URL = 'localhost:8000';` instead of `const API_BASE_URL = 'http://localhost:8000';` or `const API_BASE_URL = 'https://your-domain.org:8000';`. It can also happen if you really load something via a `file:///` URL, which can easily be checked by something like `fgreg -rni 'file://' frontend/` in the shell.
* I get a similar error as above, but in the console I see the reason given as something like `Mixed Content: The page at 'page' was loaded over HTTPS, but requested an insecure resource` or similar, depending on the browser used. Why?
    - You have most likely configured SSL/HTTPS for your website, but the frontend loads some resources via a HTTP scheme. E.g., the frontend is accessible at https://your-domain.org/pa/, but it connects to a backend API URL configured as `API_BASE_URL = 'http://localhost:8000'` instead of `https://localhost:8000'`. It could also be any other resource you load, like a javascript file sourced from a remote server via a HTTP scheme instead of HTTPS.
* I see a CORS error in the browser console that says the origin is not allowed. What is wrong?
    - In your backend, you will need to explicitely allow requests from your frontend domain. This is configured in [backend/api.py](./backend/api.py) at the top, in a function call to `app.add_middleware()`, in a line that looks like `allow_origins=["http://localhost:3000"]`. You will need to adapt this line to your backend scheme and location, e.g., in production, when the frontend is accessible to users at `https://your-domain.org/pa/`, this needs to be `allow_origins=["https://your-domain.org"]`. Note that CORS origins are a combination of scheme, host, and optionally port, but do not include the path (the `/pa/` in this case).


## Deployment options

There are many deployment strategies, you can read about one option for deployment directly on Linux (without Docker) in [DEPLOYMENT_LINUX.md](./DEPLOYMENT_LINUX.md).

