from kubernetes import client, config

config.load_kube_config()

def deploy():
    pass

# v1 = client.CoreV1Api()

# print("listing all pods with their IPs:")
# ret = v1.list_pod_for_all_namespaces(watch=False)
# for item in ret.items:
#     print("%s\t%s\t%s" % (item.status.pod_ip, item.metadata.namespace, item.metadata.name))

# apps_v1 = client.AppsV1Api()
# apps_v1.create_namespaced_deployment(body={}, namespace="", dry_run="All")
