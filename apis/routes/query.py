from fastapi import APIRouter

from celery.result import AsyncResult
from apis.models.remote_host import RemoteHosts
from apis.models.settings import Settings
from apis.utils.worker_manager import manager
from apis.utils.setting import setting_manager


query_route = APIRouter()

@query_route.get("/apis/v1/query_task")
async def query_task(task_id: str):
    return AsyncResult(task_id).result


@query_route.post(
    path="/apis/v1/add_update_worker",
    summary="Add or update worker to the system",
    tags=["Setting"]
)
async def add_worker(remote_hosts: RemoteHosts) -> list:
    result = []
    for host in remote_hosts.hosts:
        result.append(manager.add_update_worker(host))
    return result


@query_route.get(
    path="/apis/v1/get_workers",
    summary="Get worker info",
    response_model=RemoteHosts,
    tags=["Setting"]
)
async def get_workers(host_name: str = "all") -> RemoteHosts:
    return manager.get_workers(host_name)


@query_route.get(
    path="/apis/v1/remove_worker",
    summary="Remove worker from the system",
    tags=["Setting"]
)
async def remove_worker(host_name: str) -> bool:
    return manager.remove_worker(host_name)

@query_route.get(
    path="/apis/v1/save_setting",
    summary="Save setting to the system",
    tags=["Setting"]
)
async def save_setting(settings: Settings) -> bool:
    return setting_manager.add_update_setting(settings)

@query_route.get(
    path="/apis/v1/get_setting",
    summary="Get setting from the system",
    tags=["Setting"]
)
async def get_setting(setting_id: str) -> Settings:
    return setting_manager.get_setting(setting_id)
