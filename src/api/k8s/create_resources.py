import json
from dataclasses import dataclass
from typing import Optional, Union

from kubernetes import config, client


config.load_kube_config()

k8s_core_v1 = client.CoreV1Api()
k8s_apps_v1 = client.AppsV1Api()


@dataclass
class DeploymentResult():
    result: bool
    info: Optional[Union[str, dict, list]] = None


def deploy_one(resource_type: str,
               data: dict,
               target_namespace: str) -> str:

    if resource_type == "deployment":
        resp = k8s_apps_v1.create_namespaced_deployment(
            body=data,
            namespace=target_namespace
        )
    elif resource_type == "service":
        resp = k8s_core_v1.create_namespaced_service(
            body=data,
            namespace=target_namespace
        )

    return resp.metadata.name


def deploy(data: dict, target_namespace: str) -> DeploymentResult:

    resource_type = data.get("kind").lower()

    try:
        result = deploy_one(resource_type, data, target_namespace)
    except client.exceptions.ApiException as e:
        print(f"EXCEPTION! {e}")
        # body = json.loads(e.body)

        # error_details = {
        #     "message": "Deployment failed.",
        #     "causes": body["details"]["causes"]
        # }

        # return DeploymentResult(False, error_details)
        return DeploymentResult(False, "")

    return DeploymentResult(True, result)
