from apis.utils.worker_manager import manager
from tools.scheduler.scheduler import filter_hosts
from workflows.read_workflow import Workflow
from works.main import app


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
    if len(exec_hosts) == 0:
        return {"status": "Failed", "msg": "There is no host available for the execution of the task."}

    workflow = Workflow(params, task_type, exec_hosts)
    return workflow.run_task()
