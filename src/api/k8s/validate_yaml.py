import json
from dataclasses import dataclass
from typing import Optional, Union

from kubernetes import config, client


config.load_kube_config()


@dataclass
class ValidationResult():
    result: bool
    reason: Optional[Union[str, dict, list]] = None


def create_resource(core_client: client.CoreV1Api,
                    apps_client: client.AppsV1Api,
                    resource_type: str,
                    data: dict,
                    target_namespace: str) -> Union[str, ValidationResult]:

    if resource_type.lower() == "deployment":
        resp = apps_client.create_namespaced_deployment(
            body=data,
            namespace=target_namespace,
            dry_run="All"
        )
    elif resource_type.lower() == "service":
        resp = core_client.create_namespaced_service(
            body=data,
            namespace=target_namespace,
            dry_run="All"
        )
    else:
        return ValidationResult(
            False, f"Resource type not supported: {resource_type}")

    return resp.metadata.name


def validate(data: dict, target_namespace: str) -> ValidationResult:
    k8s_core_v1 = client.CoreV1Api()
    k8s_apps_v1 = client.AppsV1Api()

    namespaces = k8s_core_v1.list_namespace()
    namespace_names = [
        namespace.metadata.name for namespace in namespaces.items]

    if target_namespace not in namespace_names:
        k8s_core_v1.create_namespace(client.V1Namespace(
            metadata=client.V1ObjectMeta(name=target_namespace)))

    resource_type = data.get("kind", None)

    if resource_type is None:
        return ValidationResult(False, "Missing 'kind' field.")

    try:
        create_resource(k8s_core_v1, k8s_apps_v1,
                        resource_type, data, target_namespace)
    except client.exceptions.ApiException as e:
        body = json.loads(e.body)

        error_details = {
            "message": "YAML file validation failed.",
            "causes": body["details"]["causes"]
        }

        return ValidationResult(False, error_details)

    return ValidationResult(True)
