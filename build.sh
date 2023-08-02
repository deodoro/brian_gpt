echo "Cleaning up"
mkdir -p build
rm -rf build/*
cp docker/Dockerfile build
cp docker/env build
echo "Copying server files"
cp server/*.py server/requirements.txt build
echo "Building client"
cd client
docker build -t react-builder .
echo "Deploying client"
cd ../build
container=$(docker create react-builder)
docker cp $container:/app/dist ./
echo "Building server"
docker build -t q_and_a .
echo "Done"
cd ..
