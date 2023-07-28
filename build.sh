rm -rf docker/*.py docker/requirements.txt docker/dist
cp chat-server-py/*.py docker
cp chat-server-py/requirements.txt docker
API_URL=/chat/api npm run build --prefix client
mv client/dist docker/
cd docker
docker build -t q_and_a .
