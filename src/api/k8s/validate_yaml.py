import json
import os
from dataclasses import dataclass
from typing import Optional, Union

from kubernetes import client, config

if os.getenv("KUBERNETES_SERVICE_HOST") is None:
    config.load_kube_config()
else:
    config.load_incluster_config()


k8s_core_v1 = client.CoreV1Api()
k8s_apps_v1 = client.AppsV1Api()


@dataclass
class ValidationResult():
    result: bool
    reason: Optional[Union[str, dict, list]] = None


def validate_one(resource_type: str,
                 data: dict,
                 target_namespace: str) -> Union[str, ValidationResult]:

    if resource_type.lower() == "deployment":
        resp = k8s_apps_v1.create_namespaced_deployment(
            body=data,
            namespace=target_namespace,
            dry_run="All"
        )
    elif resource_type.lower() == "service":
        resp = k8s_core_v1.create_namespaced_service(
            body=data,
            namespace=target_namespace,
            dry_run="All"
        )
    else:
        return ValidationResult(
            False, f"Resource type not supported: {resource_type}")

    return resp.metadata.name


def validate(data: dict, target_namespace: str) -> ValidationResult:

    resource_type = data.get("kind", None)

    if resource_type is None:
        return ValidationResult(False, "Missing 'kind' field.")

    try:
        validate_one(resource_type, data, target_namespace)
    except client.exceptions.ApiException as e:
        body = json.loads(e.body)

        error_details = {
            "message": "YAML file validation failed.",
            "causes": body["details"]["causes"]
        }

        return ValidationResult(False, error_details)

    return ValidationResult(True)
