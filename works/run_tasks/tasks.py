import json
import os

from tools.scheduler.scheduler import filter_hosts
from works.main import app
from tools.logger import common_logger
from apis.utils.worker_manager import manager


@app.task()
def run_task(
        params: object,
        task_type: str,
) -> dict:
    """
    Run a task.
    :param params: The parameters of the task.
    :param task_type: The type of the task.
    :return: The result of the task.
    """
    hosts = manager.get_workers().hosts
    exec_hosts = filter_hosts(hosts, params.filter_hosts)
    return {}
