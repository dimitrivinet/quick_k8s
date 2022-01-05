"""Router for manipulating resources."""

from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
import yaml  # type: ignore

from app import k8s, database
from app.utils import auth
from app.config import cfg


router = APIRouter(prefix="/resources", tags=["k8s"])


@router.get("/")
async def get_all_resources(
    _: auth.UserInDB = Depends(auth.current_user_is_admin),
):
    all_resources = k8s.resources.get_all_resources(cfg.TARGET_NAMESPACE)
    print(all_resources._asdict())

    return all_resources._asdict()


@router.get("/deployments")
async def get_all_deployments(
    _: auth.UserInDB = Depends(auth.current_user_is_admin),
):
    deployment_list = k8s.resources.get_all_deployments(cfg.TARGET_NAMESPACE)

    return deployment_list


@router.get("/services")
async def get_all_services(
    _: auth.UserInDB = Depends(auth.current_user_is_admin),
):
    service_list = k8s.resources.get_all_services(cfg.TARGET_NAMESPACE)

    return service_list


@router.post("/")
async def create_resource(
    yaml_file: UploadFile = File(...),
    # namespace_exists: None = Depends(k8s.check_namespace(TARGET_NAMESPACE)),
    current_user: auth.User = Depends(auth.get_current_active_user),
):
    # print(f"{current_user=}")

    filename = yaml_file.filename

    # listify generator because we need to use it multiple times
    yamls_as_dicts = list(yaml.safe_load_all(yaml_file.file))

    # validate docs
    for doc in yamls_as_dicts:
        validation_result = k8s.validate(doc, cfg.TARGET_NAMESPACE)

        if not validation_result.result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_result.reason,
            )

    owner = database.users.get_user(current_user.username)
    owner_id = owner.id  # type: ignore

    # deploy docs
    deployed = []
    for doc in yamls_as_dicts:
        deployment_result = k8s.deploy(doc, cfg.TARGET_NAMESPACE)

        if not deployment_result.result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=deployment_result.reason,  # type: ignore
            )

        deployed_type = deployment_result.info.kind  # type: ignore
        deployed_name = deployment_result.info.metadata.name  # type: ignore
        deployed.append({"name": deployed_name, "type": deployed_type})

        new_resource = database.orm.Resource(
            owner=owner_id,
            name=deployed_name,
            type=deployed_type,
            created_timestamp=datetime.now(),
        )

        database.resources.add_resource(new_resource)

    return {"deployed": deployed, "filename": filename}


@router.delete("/{resource_type}/{resource_name}")
def delete_deployment(
    resource_type: str,
    resource_name: str,
    current_user: auth.User = Depends(auth.get_current_active_user),
):
    user_db = database.users.get_user(current_user.username)

    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknow user in database. (user: {current_user.username})",
        )

    resource_db = database.resources.get_resource(resource_name, user_db.id)
    if resource_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(f"Unknown resource {resource_name} in database."),
        )

    if resource_db.type.lower() != resource_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Expected resource of type {resource_type}"
                f" but got resource of type {resource_db.type.lower()}"
            ),
        )

    ret, reason = k8s.resources.delete_resource(
        resource_name,
        resource_type,
        cfg.TARGET_NAMESPACE,
    )

    if ret == "Failure":
        return {"status": ret, "reason": reason}

    database.resources.fake_delete_resource(resource_db)

    return {"status": ret, "reason": reason}


@router.post("/{resource_type}/{resource_name}")
def update_deployment_dummy(
    resource_name: str,
    current_user: auth.User = Depends(auth.get_current_active_user),
):
    user_db = database.users.get_user(current_user.username)

    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknow user in database. (user: {current_user.username})",
        )

    new_timestamp = datetime.now()
    database.resources.set_update_time(
        resource_name,
        user_db.id,
        new_timestamp,
    )
