"""API for listing and deleting resources in the cluster."""

import os
from typing import NamedTuple, Tuple, List

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from kubernetes.client.models.v1_status import V1Status

if os.getenv("KUBERNETES_SERVICE_HOST") is None:
    config.load_kube_config()
else:
    config.load_incluster_config()

k8s_core_v1 = client.CoreV1Api()
k8s_apps_v1 = client.AppsV1Api()


class ResourceList(NamedTuple):
    deployments: List[dict]
    services: List[dict]


def get_all_resources(namespace_name: str) -> ResourceList:
    return ResourceList(
        deployments=get_all_deployments(namespace_name),
        services=get_all_services(namespace_name),
    )


def get_all_services(namespace_name: str) -> List[dict]:
    services = k8s_core_v1.list_namespaced_service(
        namespace=namespace_name, pretty="false"
    )

    ret = []

    services_list = services.items
    for service in services_list:
        ret.append(service.metadata.name)

    return ret


def get_all_deployments(namespace_name: str) -> List[dict]:
    deployments = k8s_apps_v1.list_namespaced_deployment(
        namespace=namespace_name, pretty="false"
    )

    ret = []

    deployments_list = deployments.items
    for deployment in deployments_list:
        ret.append(deployment.metadata.name)

    return ret


def delete_resource(
    resource_name: str, resource_type: str, namespace_name: str
) -> Tuple[str, str]:
    if resource_type == "deployment":
        return delete_deployment(resource_name, namespace_name)

    if resource_type == "service":
        return delete_service(resource_name, namespace_name)

    return "Failure", f"Unknown resource type {resource_type}"


def delete_deployment(
    deployment_name: str,
    namespace_name: str,
) -> Tuple[str, str]:
    try:
        ret: V1Status = k8s_apps_v1.delete_namespaced_deployment(
            deployment_name, namespace_name
        )
    except ApiException as e:
        return "Failure", e.reason

    return ret.status, ret.reason


def delete_service(service_name: str, namespace_name: str) -> Tuple[str, str]:
    try:
        ret: V1Status = k8s_core_v1.delete_namespaced_service(
            service_name, namespace_name
        )
    except ApiException as e:
        return "Failure", e.reason

    return ret.status, ret.reason
