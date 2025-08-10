# Multi-stage build: build React with Node, run Flask with Python

# ---- Frontend build stage ----
FROM node:18-alpine AS frontend
WORKDIR /app

# Install deps first (better layer caching)
COPY package.json package-lock.json ./
RUN npm ci

# Copy sources and build
COPY public ./public
COPY src ./src
COPY tailwind.config.js postcss.config.js ./
ENV NODE_OPTIONS=--max_old_space_size=512
RUN npm run build

# ---- Backend runtime stage ----
FROM python:3.11-slim AS backend
WORKDIR /app

# System deps (optional: uncomment if reportlab or other libs require them)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libjpeg62-turbo \
#     && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt ./
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Copy built frontend into /app/build for Flask to serve
COPY --from=frontend /app/build ./build

ENV PORT=8000
EXPOSE 8000
CMD ["python", "backend/run_backend.py"]


