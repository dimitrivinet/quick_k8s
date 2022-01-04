IM_NAME=dimitrivinet/quick-k8s-v2
IM_TAG=dev

all: build push

run_api:
	cd src && uvicorn app.main:app --reload

run:
	docker run -it --rm ${IM_NAME}:${IM_TAG} bash

build:
	docker build -t ${IM_NAME}:${IM_TAG} ./src

push:
	docker push ${IM_NAME}:${IM_TAG}

refresh_deployment:
	kubectl delete -f k8s/deployment.yml
	kubectl apply -f k8s/deployment.yml
