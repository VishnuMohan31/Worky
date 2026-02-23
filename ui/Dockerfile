# =========================
# Stage 1: Build
# =========================
FROM node:18-alpine AS builder

# Build arguments for environment variables
ARG VITE_API_BASE_URL
ARG VITE_API_TIMEOUT=30000

WORKDIR /app

# Install bash (for scripts if needed) and dos2unix to fix line endings
RUN apk add --no-cache bash dos2unix

# Copy package files first to leverage caching
COPY package*.json ./

# Install dependencies in a reproducible way
RUN npm ci --legacy-peer-deps

# Copy the rest of the source code
COPY . .

# Remove any .env files to prevent interference
RUN rm -f .env .env.* || true

# Fix line endings and make all scripts executable
RUN find . -type f -name "*.sh" -exec dos2unix {} \; \
    && chmod -R +x node_modules/.bin

# Set environment variables for build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_API_TIMEOUT=$VITE_API_TIMEOUT

# Verify environment variables
RUN echo "Building UI with API URL: $VITE_API_BASE_URL and timeout: $VITE_API_TIMEOUT"

# Build the production-ready frontend
RUN npm run build:prod

# =========================
# Stage 2: Production
# =========================
FROM node:18-alpine AS production

WORKDIR /app

# Install bash (optional) and serve for static files
RUN apk add --no-cache bash && npm install -g serve

# Copy built files from builder stage
COPY --from=builder /app/dist ./dist

# Expose port 80
EXPOSE 80

# Serve static files
CMD ["serve", "-s", "dist", "-l", "80"]
