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
cd ~/personal-analytics/
cp frontend/* /var/www/your-domain.org/html/pa/ # may need to do this as another user or with sudo, depending on who owns /var/www/your-domain.org/html
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
        auth_basic "Restricted Area";
        auth_basic_user_file /etc/nginx/.htpasswd;
        try_files $uri $uri/ =404;
    }

    # more stuff here maybe, like your certbot/SSL configuration
}
```

If you now restart nginx and connect to https://your-domain.org/pa, you should see the frontend. If you configured password protection, you should be asked for HTTP basic authentication to "Restricted Area", and after you provide `yourwebusername` and `yourwebpassword`, you will see it.


## Deployment Part II -- Backend

The most critical part if the backend. You should create a system service for it, along with a dedicated user.

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
