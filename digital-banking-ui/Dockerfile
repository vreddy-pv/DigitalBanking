# ==============================================================================
# Stage 1: Builder - Build the Angular application
# ==============================================================================
FROM node:18-alpine AS builder

LABEL stage=builder
LABEL description="Build stage for Digital Banking UI"

# Set working directory
WORKDIR /app

# Copy entire workspace first (excluding node_modules, dist, etc which are in .dockerignore)
COPY . .

# Install dependencies
RUN npm install --legacy-peer-deps --no-audit

# Build the Angular app for production
RUN npm run build -- --configuration production

# Optional: Verify build artifacts
RUN ls -la dist/

# ==============================================================================
# Stage 2: Runtime - Serve the built application
# ==============================================================================
FROM node:18-alpine AS runtime

LABEL description="Runtime stage for Digital Banking UI"
LABEL maintainer="Digital Banking Team"

# Install serve package for serving static files
RUN npm install -g serve

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
