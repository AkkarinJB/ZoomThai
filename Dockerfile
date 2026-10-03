FROM node:20-slim AS builder
WORKDIR /app
COPY api/package.json api/package-lock.json ./api/
WORKDIR /app/api
RUN npm ci
COPY api/ ./
RUN npm run build

FROM node:20-slim
WORKDIR /app/api
COPY --from=builder /app/api/package.json ./
COPY --from=builder /app/api/node_modules ./node_modules
COPY --from=builder /app/api/dist ./dist
EXPOSE 3000
CMD ["npm", "start"]
