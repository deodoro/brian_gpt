FROM node:14
WORKDIR /app
COPY ./package*.json ./
RUN npm install
COPY ./src ./src
RUN API_URL=/chat/api npm run build
