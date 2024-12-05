from works.main import app


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
