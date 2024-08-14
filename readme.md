
PS C:\Users\shiva> docker network create m-network
047b67dedf113b602d88ced383b911568adc51d3b0f044d2caac0ae810de8175

Setup mango reference: https://hub.docker.com/_/mongo
docker run -d --network m-network --name raj-mongo \
	-e MONGO_INITDB_ROOT_USERNAME=mongoadmin \
	-e MONGO_INITDB_ROOT_PASSWORD=secret \
	mongo




**To get the docker ip address
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mongo

To debug the mongo connection using mongo scanner
install mongo scannet

mongosh command: mongodb://root:example@localhost:27017/?authSource=admin

docker-compose -f .\mongo-docker-compose.yml up -d
docker-compose -f .\mongo-docker-compose.yml down
