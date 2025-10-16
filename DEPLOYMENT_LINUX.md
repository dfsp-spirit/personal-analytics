## Deployment of personal-analytics to Production under Linux -- One Example Setup

### Prerequisites

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

### Deployment overview

We are going for direct deployment on the machine without Docker.

We will be running everything on this machine:

* The frontend (pure JS/HTML/CSS): will be served statically be nginx
* The backend (python package): will be installed into a virtual environment and served by uvicorn. It is deployed as a system service with auto-restart, auto-start on boot, etc.
* The database: the postgresql database server will be running on the system. We will create a dedicated database and database user for this app.



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
