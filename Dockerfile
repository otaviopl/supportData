# Frontend Dockerfile

FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install pnpm and dependencies
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN corepack enable && corepack prepare pnpm@latest --activate && pnpm install

# Copy source code
COPY frontend/ ./

# Build the Next.js app
RUN pnpm build

# Expose port and run
EXPOSE 3000
CMD ["pnpm", "start"]