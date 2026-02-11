# Multi-stage build for production
FROM node:18-alpine AS builder

# Build arguments for environment variables
# MUST be passed during docker build with --build-arg
ARG VITE_API_BASE_URL
ARG VITE_API_TIMEOUT=30000

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy source code (excluding .env files)
COPY . .

# Remove any .env files to prevent interference
RUN rm -f .env .env.local .env.production .env.development

# Set environment variables for build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_API_TIMEOUT=$VITE_API_TIMEOUT

# Verify the API URL is set correctly before building
RUN echo "Building UI with API URL: $VITE_API_BASE_URL"

# Build for production (will use ENV variables)
RUN npm run build:prod

# Production stage - serve with simple HTTP server
FROM node:18-alpine

WORKDIR /app

# Install serve package globally
RUN npm install -g serve

# Copy built files from builder
COPY --from=builder /app/dist ./dist

EXPOSE 80

# Serve the built files on port 80
CMD ["serve", "-s", "dist", "-l", "80"]



