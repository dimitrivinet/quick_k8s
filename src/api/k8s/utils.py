from kubernetes import config, client


config.load_kube_config()

k8s_core_v1 = client.CoreV1Api()
k8s_apps_v1 = client.AppsV1Api()

def check_namespace(namespace_name: str):
    def check_namespace_inner() -> None:
        namespaces = k8s_core_v1.list_namespace()
        namespace_names = [
            namespace.metadata.name for namespace in namespaces.items]

        if namespace_name not in namespace_names:
            k8s_core_v1.create_namespace(client.V1Namespace(
                metadata=client.V1ObjectMeta(name=namespace_name)))

    return check_namespace_inner
