FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install nginx and supervisor
RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx supervisor gcc build-essential \
    && rm -f /etc/nginx/sites-enabled/default \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /opt/app

# Copy the whole project into the image
COPY . /opt/app

# Install Python requirements for the FastAPI app
RUN pip install --no-cache-dir -r /opt/app/app/requirements.txt

# Move nginx config and static files into place
RUN rm -f /etc/nginx/conf.d/default.conf || true
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY nginx/html /usr/share/nginx/html

# Supervisor config
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

STOPSIGNAL SIGTERM

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
