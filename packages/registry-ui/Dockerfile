# Build stage
FROM node:20-slim AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# For development, we don't strictly need to build, but having it is good
# RUN npm run build

# Production stage (Optional, if you want a small production image)
# If using Vite dev server in Docker (common for local dev), we just use the Node image
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
