from fastapi import APIRouter

from works.main import app
from apis.models.remote_host import RemoteHosts
from apis.utils.worker_manager import manager


query_route = APIRouter()

@query_route.get("/apis/v1/query_task")
async def query_task(task_id: str):
    return


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
