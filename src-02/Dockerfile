# syntax=docker/dockerfile:1
FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1


# System deps (optional but useful for packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
&& rm -rf /var/lib/apt/lists/*


WORKDIR /app


# Install deps first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


# Copy code
COPY app ./app
COPY gunicorn_conf.py ./


EXPOSE 8000


# Run with Gunicorn + Uvicorn workers
CMD ["gunicorn", "app.main:app", "-c", "gunicorn_conf.py"]
