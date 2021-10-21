import json
import os
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from kubernetes.client.models.v1_deployment import V1Deployment
from kubernetes.client.models.v1_deployment_list import V1DeploymentList
import yaml

from app import dummy_db, k8s
from app.utils import auth


TARGET_NAMESPACE = os.getenv("TARGET_NAMESPACE", "")

router = APIRouter(prefix="/k8s", tags=["k8s"])


class DeploymentEncoder(json.JSONEncoder):
    def default(self, obj):
        return repr(obj)


@router.get("/deployments")
async def get_all_deployments():
    deployment_list: V1DeploymentList = k8s.get_all_deployments(TARGET_NAMESPACE)
    # print(json.dumps(deployments.to_dict(), cls=DeploymentEncoder))
    # print(type(deployments))
    deployments: List[V1Deployment] = deployment_list.items

    return {"deployments": [deployment.metadata.name for deployment in deployments]}


@router.post("/deployments")
async def create_deployment(
    yaml_file: UploadFile = File(...),
    # namespace_exists: None = Depends(k8s.check_namespace(TARGET_NAMESPACE)),
    current_user: auth.User = Depends(auth.get_current_active_user),
):
    # print(f"{current_user=}")

    filename = yaml_file.filename

    # listify generator because we need to use it multiple times
    yamls_as_dicts = list(yaml.safe_load_all(yaml_file.file))

    for doc in yamls_as_dicts:
        validation_result = k8s.validate(doc, TARGET_NAMESPACE)

        if not validation_result.result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=validation_result.reason
            )

    deployed = []
    for doc in yamls_as_dicts:
        # print(doc)
        deployment_result = k8s.deploy(doc, TARGET_NAMESPACE)

        if not deployment_result.result:
            raise HTTPException(
                # pylint: disable=no-member
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=deployment_result.reason,  #  type: ignore
            )

        deployed_name = deployment_result.info.metadata.name  # type: ignore
        deployed.append(deployed_name)
        # print(deployment_result)

        if current_user.username not in dummy_db.user_deployments:
            dummy_db.user_deployments[current_user.username] = []

        dummy_db.user_deployments[current_user.username].append(deployed_name)

    return {"deployed": deployed, "filename": filename}


@router.delete("/deployments/{deployment_name}")
def delete_deployment(deployment_name: str):
    ret, reason = k8s.delete_deployment(deployment_name, TARGET_NAMESPACE)

    return {"status": ret, "reason": reason}
