import os
from typing import Tuple

from kubernetes import client, config
from kubernetes.client.models.v1_status import V1Status
from kubernetes.client.exceptions import ApiException

if os.getenv("KUBERNETES_SERVICE_HOST") is None:
    config.load_kube_config()
else:
    config.load_incluster_config()

UNTOUCHABLE_DEPLOYMENTS = ["quick-k8s-manager-deployment"]

k8s_apps_v1 = client.AppsV1Api()

def get_all_deployments(namespace_name: str):
    deployments = k8s_apps_v1.list_namespaced_deployment(namespace=namespace_name, pretty="false")

    return deployments

def delete_deployment(deployment_name: str, namespace_name: str) -> Tuple[str, str]:
    if deployment_name in UNTOUCHABLE_DEPLOYMENTS:
        return "Failure", "Not Authorized."

    try:
        ret: V1Status = k8s_apps_v1.delete_namespaced_deployment(deployment_name, namespace_name)
    except ApiException as e:
        return "Failure", e.reason

    return ret.status, ret.reason
