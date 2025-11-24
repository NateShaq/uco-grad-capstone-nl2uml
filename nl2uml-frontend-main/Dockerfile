# --- build stage ---
FROM node:18-alpine AS build
WORKDIR /app

COPY package*.json ./
# If lock is out of sync, switch to `npm install` or re-gen lock locally.
RUN npm ci

COPY . .
# Bake the backend URL into the static build (CRA reads REACT_APP_* at build time)
ARG REACT_APP_API_BASE=http://localhost:8080
ENV REACT_APP_API_BASE=$REACT_APP_API_BASE
RUN npm run build

# --- runtime stage ---
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx","-g","daemon off;"]
