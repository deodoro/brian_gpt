FROM node:14
WORKDIR /app
COPY ./package*.json ./
RUN npm install
COPY ./src ./src
RUN REACT_APP_API_URL=/chat/api npm run build
