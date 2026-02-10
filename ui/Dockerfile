# Multi-stage build for production
FROM node:18-alpine AS builder

# Build arguments for environment variables
ARG VITE_API_BASE_URL=http://62.171.191.132:8007/api/v1
ARG VITE_API_TIMEOUT=30000

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Set environment variables for build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_API_TIMEOUT=$VITE_API_TIMEOUT

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



