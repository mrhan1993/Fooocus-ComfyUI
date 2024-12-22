import json
import os

from works.main import app
from tools.logger import common_logger


@app.task()
def run_task(
        params: dict,
        task_type: str,
) -> dict:
    """
    Run a task.

    :param params: The parameters of the task.
    :param task_type: The type of the task.
    :return: The result of the task.
    """
    pass
