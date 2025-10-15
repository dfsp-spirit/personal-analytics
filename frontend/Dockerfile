FROM nginx:alpine

# Copy frontend files
COPY . /usr/share/nginx/html/
COPY config.docker.js /usr/share/nginx/html/config.js

# Copy custom nginx config (optional)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]