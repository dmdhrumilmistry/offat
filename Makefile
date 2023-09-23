build-local-images:
	@docker build -f DockerFiles/base-Dockerfile -t dmdhrumilmistry/offat-base .
	@docker build -f DockerFiles/cli-Dockerfile -t dmdhrumilmistry/offat .
	@docker build -f DockerFiles/api-base-Dockerfile -t dmdhrumilmistry/offat-api-base .
	@docker build -f DockerFiles/api-Dockerfile -t dmdhrumilmistry/offat-api .
	@docker build -f DockerFiles/worker-Dockerfile -t dmdhrumilmistry/offat-api-worker .

