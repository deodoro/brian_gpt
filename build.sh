echo "Cleaning up"
rm -rf build/*.py build/requirements.txt build/dist
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
