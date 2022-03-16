# Makefile for standalone Music service (S2)

VER=v1

SERVER1=`docker inspect s1 --format '{{.NetworkSettings.IPAddress}}'`
SERVER2=`docker inspect s2 --format '{{.NetworkSettings.IPAddress}}'`

PORT=30001
SERVICE=user
build-mcli:
	docker image build -f Dockerfile -t mcli:$(VER) .

run-mcli:
	docker container run -it --rm --name mcli mcli:$(VER) python3 mcli.py $(SERVER1) $(PORT) $(SERVICE)
