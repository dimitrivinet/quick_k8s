import os

from fastapi import APIRouter, File, HTTPException, UploadFile, status
import yaml

from app import k8s

TARGET_NAMESPACE = os.getenv("TARGET_NAMESPACE", "")

router = APIRouter(prefix="/k8s", tags=["k8s"])


@router.post("/deployments", tags=["k8s"])
async def create_deployment(
    yaml_file: UploadFile = File(...),
    # namespace_exists: None = Depends(k8s.check_namespace(TARGET_NAMESPACE)),
    # current_user: User = Depends(get_current_active_user),
):
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
        print(doc)
        deployment_result = k8s.deploy(doc, TARGET_NAMESPACE)

        if not deployment_result.result:
            raise HTTPException(
                # pylint: disable=no-member
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=deployment_result.reason,  #  type: ignore
            )

        deployed.append(deployment_result.info)
        print(deployment_result)

    return {"deployed": deployed, "filename": filename}
