# ---------- FRONTEND BUILD ----------
FROM node:18 AS frontend-build
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build


# ---------- BACKEND BUILD ----------
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

# copy entire backend
COPY . .

# copy built frontend → Django staticfiles dirs (will be collected to STATIC_ROOT)
COPY --from=frontend-build /app/frontend/dist /app/nft_lottery/nft_lottery/static/frontend/

# set working directory to Django project root
WORKDIR /app/nft_lottery

# Create base media directory (Django will create subdirectories automatically)
RUN mkdir -p media

# collect static once here
RUN python manage.py collectstatic --noinput
