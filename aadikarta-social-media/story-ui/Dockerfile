FROM nginx:alpine

# Copy static assets to nginx html directory
COPY . /usr/share/nginx/html

# Replace default nginx config with our custom one to proxy webhook
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Default command is already appropriate for nginx:alpine
