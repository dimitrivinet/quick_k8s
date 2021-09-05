IM_NAME=dimitrivinet/quick-k8s-v2
IM_TAG=dev

run_api:
	uvicorn src.api.main:app --reload

build:
	docker build -t ${IM_NAME}:${IM_TAG} ./src

push:
	docker push ${IM_NAME}:${IM_TAG}
