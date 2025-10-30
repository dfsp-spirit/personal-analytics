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

We are going for direct deployment on the machine. This will work on bare meta, a VM, or a virtual server.

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
cp -r ~/personal-analytics/frontend/* /var/www/your-domain.org/html/pa/ # your user should own /var/www/your-domain.org/, so you should NOT need sudo for this.
vim /var/www/your-domain.org/html/pa/settings.js # adapt the API_BASE_URL to your server. We will assume https://your-domain.org/pa_backend in this document.
```

Now let us make sure the permissions for the web directory are correct: the files are owned by your user, but the group gives the nginx user (`www-data` under Debian/Ubuntu) read permissions.

```sh
sudo chown -R $USER:www-data /var/www/your-domain.org/html/pa
sudo find /var/www/your-domain.org/html/pa -type d -exec chmod 755 {} \;
sudo find /var/www/your-domain.org/html/pa -type f -exec chmod 644 {} \;
```
NOTE: The setup implemented by the commands above does **not** allow nginx to write to files in the web directory of the personal analytics app, `html/pa/`. This is a secure setup for our app, which does not require any uploads to the server, or the server writing some form of other files to the web directory.


If you want, setup password protection for that directory. Come up with a suitable username and password, then:

```sh
sudo apt install apache2-utils # for htpasswd, does NOT install apache2 server.
sudo htpasswd -c /etc/nginx/.htpasswd yourwebusername # will ask for yourwebpassword
sudo chown root:www-data /etc/nginx/.htpasswd
sudo chmod 640 /etc/nginx/.htpasswd
```

Then, in your nginx configuration, most likely at `/etc/nginx/sites-available/your-domain.org`, you would have something like this for the frontend:

```sh
server {
    server_name your-domain.org www.your-domain.org;

    root /var/www/your-domain.org/html;
    index index.html;

    # your existing public website, if you already have one.
    location / {
        try_files $uri $uri/ =404;
        # Here follow general security settings
    }

    # personal-analytics frontend
    location /pa/ {
        auth_basic "PersonalAnalytics";
        auth_basic_user_file /etc/nginx/.htpasswd;
        try_files $uri $uri/ =404;
        # Security recommendations specific to the /pa/ location:
        # - Rate limiting (limit_req with limit_req_zone in http context)
        # - Security headers:
        #   add_header X-Frame-Options "SAMEORIGIN" always;
        #   add_header X-Content-Type-Options "nosniff" always;
        #   add_header X-XSS-Protection "1; mode=block" always;
        #   server_tokens off;
        # - Other nginx security best practices
    }

    # Here follows the backend service later, see below.

    # Here follow general security settings of this server, like:
    #  - your certbot/SSL configuration
    #  - rate limiting
    #  - restricting accessible file types
    #  - ...
}
```

Note: This nginx configuration is app-specific only and does not address general server security. Ensure your production nginx setup includes proper SSL, rate limiting, and other security hardening measures.

If you now restart nginx and connect to https://your-domain.org/pa, you should see the frontend. If you configured password protection, you should be asked for HTTP basic authentication for the realm "PersonalAnalytics", and after you provide `yourwebusername` and `yourwebpassword`, you will see it.


## Deployment Part II -- Backend (including Database)

The most critical part is the backend.

We will create a system service for it, along with a dedicated user, that ensure the service is:

* run in a secure and isolated way by a dedicated system user
* automatically run at boot
* automatically restarted when it is stopped for other reasons

**IMPORTANT**: The backend must **never** be stored in a directory under your web root directory, and the backend WSGI server must **never** run on a public interface.

Create the installation directory for the backend application and copy the files there:

```sh
# Copy backend app to installation directory, we will use /opt/pa-backend/
sudo mkdir -p /opt/pa-backend
sudo cp -r ~/personal-analytics/backend/* /opt/pa-backend
sudo cp ~/personal-analytics/backend/env.example /opt/pa-backend/.env
sudo vim /opt/pa-backend/.env # Adapt settings in here, like database credentials.
```

NOTE: Now we have the data for the backend in the app directory, but the app is not installed yet: we have not run pip to install the dependencies, like the WSGI server. We will do that later, after we have created a separate user that will run the app.

Let us continue with the database setup first. Ensure you have a postgresql server running in a production setup.

```sh
sudo apt install postgresql
```

Make sure you have hardened your postgresql installation for production, e.g., you may want to:

* Change the postgres database user password
* Configure `pg_hba.conf` to reject external connections: set listen_addresses = 'localhost'
* Set up firewall rules that additionally deny access to the postgresql port
* Set up proper file permissions, e.g., hide database config files in /etc/ from normal users
* Configure logging (and monitor the logs)
* Think about and create a regular backup procedure

Then run the script to create the application-specfic database and the database user that comes with the backend.

The script uses sudo to change to the postgresql system user and then uses postgresql peer auth to connect to the
database server as the database root user `postgres`. As this user, it creates the database, database user and password used by personal analytics.

You need to run this script as root, or as a user that is allowed to sudo to the postgres systems user.

NOTE: This script will set the database credentials you defined earlier in `/opt/pa-backend/.env`, so ensure they are strong and unique to this application. If you did not adapt them, you are now using the password that is public on the internet, in the source code of this repo, and your server may get compromized.

```sh
sudo chmod +x /opt/pa-backend/setup_db.sh
sudo /opt/pa-backend/setup_db.sh
```

Now that we have the database ready, let us create a dedicated system user who will run the backend app and adapt the file system permissions accordingly.

```sh
# Create dedicated system user with minimal privileges
sudo adduser --system --group --shell /usr/sbin/nologin pa-user

# Set secure file system permissions for the app dir
sudo chown -R pa-user:pa-user /opt/pa-backend/
sudo chmod -R 755 /opt/pa-backend/
sudo chmod 600 /opt/pa-backend/.env # protect secrets


# Since the user has no home and cannot login, but needs to run uv, which needs a cache directory (that by default gets created in the user home),
# we need to do some extra gymnastics and create a cache directory elsewhere for the user. The proper place is /var/cache/.
sudo mkdir -p /var/cache/pa-user/
sudo chown pa-user:pa-user /var/cache/pa-user/

# Switch to service user and install app in the service directory
cd /opt/pa-backend
sudo -u pa-user UV_CACHE_DIR=/var/cache/pa-user/ uv venv   # will create a virtual environment at /opt/pa-backend/.venv
sudo -u pa-user UV_CACHE_DIR=/var/cache/pa-user/ uv pip install -e .   # will install into the .venv
```

Ensure you can start the backend manually:

```sh
# Test running the backend standalone, without the service. (make sure to stop it with Ctrl+C when done)
sudo -u pa-user UV_CACHE_DIR=/var/cache/pa-user/ uv run uvicorn personal_analytics_backend.api:app --host 127.0.0.1 --port 8000
```

Once that works, setup a system service. E.g., for Ubuntu, copy the template service file from this repo, adapt it to your system and service user, then start it with systemctl. E.g.,


```sh
sudo cp backend/deployment/personal-analytics.service.template /etc/systemd/system/pa-backend
sudo vim /etc/systemd/system/pa-backend  # Adapt user, security, path to the software and venv you created during installation, etc. Required.
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
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
```

This tells nginx to route any requests for `https://your-domain.org/pa_backend` to the uvicorn server if they passed authentication.

You should now have nginx verify its settings and restart it.

Note that we also protected the backend with HTTP basic auth, using the *same realm* as for the frontend. Using the same realm ensures that the browser will send the realm authentication data (`yourwebusername` and `yourwebpassword`, as configured during the frontend setup) which it had to send in order to access the frontend in the first place also to the backend automatically, so users of the frontend do not even notice this.

If someone was to discover the endpoint though (guess the URL), and try to use it without the frontend (circumvent the frontend via curl, wget, whatever), they would need to provide authentication headers in their request.

Note that users connect to your website ONLY via the standard web ports 80/443 (HTTP/HTTPS), and never directly to uvicorn and port 8000, of course. So there is no need to open your firewall to the internet on that port: leave port 8000/TCP closed. If your webserver worked before, there is no need to mess with any firewall rules.

