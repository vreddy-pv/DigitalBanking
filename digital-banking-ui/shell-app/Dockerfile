# ==============================================================================
# Stage 1: Builder - Build the Angular application
# ==============================================================================
FROM node:18-alpine AS builder

LABEL stage=builder
LABEL description="Build stage for Digital Banking Shell App"

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --prefer-offline --no-audit

# Copy source code
COPY . .

# Build the Angular application for production
RUN npm run build:prod

# Optional: Verify build artifacts
RUN ls -la dist/

# ==============================================================================
# Stage 2: Runtime - Serve the built application
# ==============================================================================
FROM node:18-alpine AS runtime

LABEL description="Runtime stage for Digital Banking Shell App"
LABEL maintainer="Digital Banking Team"

# Install serve package for serving static files
RUN npm install -g serve@14.1.3

# Set working directory
WORKDIR /app

# Copy only the built artifacts from builder stage
COPY --from=builder /app/dist /app/dist

# Expose port
EXPOSE 4200

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:4200', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Set environment variables
ENV NODE_ENV=production
ENV PORT=4200

# Start the application
CMD ["serve", "-s", "dist", "-l", "4200", "--no-clipboard"]
