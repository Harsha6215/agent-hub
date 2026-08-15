FROM node:20-alpine

WORKDIR /app/apps/web

# Install dependencies — use npm install if no lock file
COPY apps/web/package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy source
COPY apps/web/ ./

EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
  CMD wget -qO- http://localhost:3000 || exit 1

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
