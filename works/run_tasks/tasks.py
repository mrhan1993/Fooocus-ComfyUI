import json
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

from apis.models.requests import CommonRequest
from apis.utils.worker_manager import manager
from apis.utils.setting import setting_manager
from tools.scheduler.scheduler import filter_hosts
from workflows.read_workflow import Workflow
from works.main import app


@app.task
def run_task(
        params: str,
        task_type: str,
        setting_id: str
) -> dict:
    """
    Run a task.
    :param params: The parameters of the task.
    :param task_type: The type of the task.
    :param setting_id: The id of the setting.
    :return: The result of the task.
    """
    params = CommonRequest(**json.loads(params))
    hosts = manager.get_workers()
    exec_hosts = filter_hosts(hosts, params.filter_hosts)
    setting = setting_manager.get_setting(setting_id)

    if len(exec_hosts) == 0:
        return {"status": "Failed", "msg": "There is no host available for the execution of the task.", "result": {}}

    work_flow = Workflow(params, task_type, setting, exec_hosts)
    result = work_flow.run_task()

    return {"status": "Success", "msg": "The task is executed successfully.", "result": result}


@app.task(ignore_result=True)
def check_worker():
    """
    Check the worker is available.
    :return: None
    """
    hosts = manager.get_workers()
    if len(hosts.hosts) == 0:
        return

    def check(host):
        ip_addr = host.host_ip
        port = host.host_port
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            r = s.connect_ex((ip_addr, port))
            s.close()
            if r != 0:
                raise ConnectionError(f"连接 {ip_addr}:{port} 失败")
            if not host.alive:
                host.alive = True
                manager.add_update_worker(host)
        except Exception:
            if host.alive:
                host.alive = False
                manager.add_update_worker(host)

    with ThreadPoolExecutor(max_workers=24) as executor:
        futures = [executor.submit(check, host) for host in hosts.hosts]
        for future in as_completed(futures):
            pass
