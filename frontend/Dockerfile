FROM node:20-alpine AS build
WORKDIR /app

# Install deps (project root context; files under frontend/)
COPY frontend/package.json frontend/package-lock.json* frontend/pnpm-lock.yaml* frontend/yarn.lock* ./
RUN if [ -f package-lock.json ]; then npm ci; elif [ -f pnpm-lock.yaml ]; then npm -g i pnpm && pnpm i --frozen-lockfile; elif [ -f yarn.lock ]; then npm -g i yarn && yarn --frozen-lockfile; else npm i; fi

# Build
COPY frontend/. .
RUN npm run build

FROM ghcr.io/nginxinc/nginx-unprivileged:1.27-alpine AS runtime
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
