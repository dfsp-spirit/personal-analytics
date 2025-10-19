# Deployment of personal-analytics to Production under Linux -- One Example Setup

## Prerequisites

This file gives an example of how to deploy the app (frontend, backend, database) on a Linux server. This would typically be a virtual machine (VM), but it doesn't matter. This suggestion assumes that:

* You have SSH or direct terminal access to a Linux machine (VM, vServer, bare metal) as root
* You are running, or can install, postgresql and nginx. You could of course use apache2 instead of nginx, but you will have to adapt the web server configuration accordingly then.
* You are familiar with running production systems in hostile environments like the internet, and know how to:
    - setup and maintain the system in a secure way
    - modify the nginx configuration
    - create postgresql databases
    - add new system users
    - create and manage system services
* The server is public on the internet and has a domain associated with it, and SSL configured, e.g., via cert-bot for nginx. Nothing of that is technically required though.
* The personal-analytics app has no authentication and no user layer. The reason is that each installation is typically customized, in the metrics it tracks, to the needs of one person. Therefore, the typical deployment will be put behind HTTP basic authentication (htpasswd) so that it is accessible from the internet (so you can fill it out from whereever you want), but still secured (so that others cannot access it even if they guess the URL on your server).

## Deployment overview

We are going for direct deployment on the machine without Docker.

We will be running everything on this machine:

* The frontend (pure JS/HTML/CSS) will be served statically be nginx

* The backend (python package): will be installed into a virtual environment and served by uvicorn. It is deployed as a system service with auto-restart, auto-start on boot, etc.
* The database: the postgresql database server will be running on the system. We will create a dedicated database and database user for this app.

## Deployment preparations

Clone the personal-analytics repo to your server, for this document we assume you put it into `~/personal-analytics/`:

```sh
cd
git clone https://github.com/dfsp-spirit/personal-analytics.git personal-analytics
```

## Deployment Part I -- Frontend

The frontend will be server as static files by nginx. If you already have a website running in nginx for your system/domain, you can simply put it into a sub directory. We will assume it is in location `/pa` for personal analytics. So if your nginx server serves your existing domain at `https://your-domain.org/`, you will be able to access the frontend at `https://your-domain.org/pa`.

We assume that on you keep your websites in `/var/www/`, as is the default under Debian/Ubuntu. Then your website would be in `/var/www/your-domain.org/html`, and you would create the sub directory `/var/www/your-domain.org/html/pa/` for the frontend. Simply copy everything from the frontend into that folder, and adapt the backend location:

```sh
cp -r ~/personal-analytics/frontend/* /var/www/your-domain.org/html/pa/ # may need to do this as another user or with sudo, depending on who owns /var/www/your-domain.org/html
vim /var/www/your-domain.org/html/pa/settings.js # adapt the API_BASE_URL to your server. We will assume https://your-domain.org/pa_backend in this document.
```

If you want, setup password protection for that directory. Come up with a suitable username and password, then:

```sh
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd yourwebusername # will ask for yourwebpassword
```

Then, in your nginx configuration, most likely at `/etc/nginx/sites-available/your-domain.org`, you would have something like this for the frontend:

```sh
server {
    server_name your-domain.org www.your-domain.org;

    root /var/www/your-domain.org/html;
    index index.html;

    # your public website, if you already have one.
    location / {
        try_files $uri $uri/ =404;
    }

    # personal-analytics frontend
    location /pa/ {
        auth_basic "PersonalAnalytics";
        auth_basic_user_file /etc/nginx/.htpasswd;
        try_files $uri $uri/ =404;
    }

    # here follows the backend service, see below

    # more stuff here maybe, like your certbot/SSL configuration
}
```

If you now restart nginx and connect to https://your-domain.org/pa, you should see the frontend. If you configured password protection, you should be asked for HTTP basic authentication for the realm "PersonalAnalytics", and after you provide `yourwebusername` and `yourwebpassword`, you will see it.


## Deployment Part II -- Backend

The most critical part if the backend. You should create a system service for it, along with a dedicated user.

Create app dir, user, and install backend there:

```sh
# Copy backend app to installation directory, we will use /opt/pa-backend/
sudo mkdir -p /opt/pa-backend
sudo cp -r ~/personal-analytics/backend/* /opt/pa-backend
sudo cp ~/personal-analytics/backend/env.example /opt/pa-backend/.env
sudo vim /opt/pa-backend/.env # Adapt settings in here.

# Create dedicated user
sudo adduser --system --group pa-user

# Set secure file system permissions for the app dir
sudo chown -R pa-user:pa-user /opt/pa-backend/
sudo chmod -R 755 /opt/pa-backend/
sudo chmod 600 /opt/pa-backend/.env # protect secrets


# Since the user has no home and cannot login, but needs to run uv, which needs a cache directory (that by default gets created in the user home),
# we need to do some extra gymnastics and create a cache directory elsewhere for the user. The proper place is /var/cache/.
mkdir -p /var/cache/pa-user/
chown pa-user:pa-user /var/cache/pa-user/

# Switch to service user and install app in the service directory
cd /opt/pa-backend
sudo -u pa-user UV_CACHE_DIR=/var/cache/pa-user/ uv venv   # will create a virtual environment at /opt/pa-backend/.venv
sudo -u pa-user UV_CACHE_DIR=/var/cache/pa-user/ uv run pip install -e .   # will install into the .venv

exit # back to your user once you are done.
```

Setup system service. E.g., for Ubuntu, copy the template service file from this repo, adapt it to your system and service user, then start it with systemctl. E.g.,


```sh
sudo cp backend/deployment/personal-analytics.service.template /etc/systemd/system/pa-backend
sudo vim /etc/systemd/system/pa-backend  # Adapt user, security, path to the software and venv you created during installation, etc. Required.
```


Check whether running the service command line you have put into the service file manually works, if we set the same environment as in the file:

```sh
sudo -u pa-user UV_CACHE_DIR=/var/cache/pa-user/ /opt/pa-backend/.venv/bin/uvicorn personal_analytics_backend.api:app --host 127.0.0.1 --port 8000
```

Now you can use standard systemctl commands to manage the service, e.g.,

```sh
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable to start on boot
sudo systemctl enable pa-backend

# Start the service now, stop it now, restart it
sudo systemctl start pa-backend
sudo systemctl stop pa-backend
sudo systemctl restart pa-backend

# Check status
sudo systemctl status pa-backend

# View logs
sudo journalctl -u pa-backend -f
```

There is one thing missing: as you have seen above, we are running uvicorn on the loopback interface only, so it is not accessible from the internet yet. We need to configure a reverse proxy in nginx, which forces users to go through nginx to reach the backend service for security reasons.

Once more, edit your nginx configuration, most likely at `/etc/nginx/sites-available/your-domain.org` and add a section like this for the backend below the frontend section we added before:

```sh
# The personal-analytics backend
    location /pa_backend/ {
        auth_basic "PersonalAnalytics";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
```

This tells nginx to route any requests for `https://your-domain.org/pa_backend` to the uvicorn server if they passed authentication.

You should now have nginx verify its settings and restart it.

Note that we also protected the backend with HTTP basic auth, using the *same realm* as for the frontend. Using the same real ensures that the browser will send the realm authentication data (`yourwebusername` and `yourwebpassword`, as configured during the frontend setup) it had to send in order to access the frontend also to the backend automatically, so users of the frontend do not even notice this.

If someone was to discover the endpoint though (guess the URL), and try to use it without the frontend (circumvent the frontend via curl, wget, whatever), they would need to provide authentication headers in their request.

Note that users connect to your website ONLY via the standard web ports 80/443 (HTTP/HTTPS), and never directly to uvicorn and port 8000, of course. So there is no need to open your firewall to the internet on that port: leave port 8000/TCP closed. If your webserver worked before, there is no need to mess with any firewall rules.

