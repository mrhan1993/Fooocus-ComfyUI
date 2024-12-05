import json
import time

import requests
from tools.logger import common_logger


def wait_for_result(task_id: str, host: str, port: int, node_id: str) -> list[dict]:
    """
    从指定的 host 根据 task_id 获取任务结果
    :param task_id: ComfyUI 的任务 ID
    :param host: 远程地址
    :param port: 远程端口
    :param node_id: 输出节点的 ID
    :return:
    """
    while True:
        try:
            state = requests.get(f"http://{host}:{str(port)}/api/history/{task_id}")
            completed = json.loads(state.text)[task_id]["status"]["completed"]
            status = json.loads(state.text)[task_id]["status"]["status_str"]
            if status == "error":
                raise RuntimeError(f"[ComfyUI] ComfyUI running error: {status}")
            if status == "success" or completed:
                return json.loads(state.text)[task_id]["outputs"][node_id]["images"]
            time.sleep(3)
        except Exception as e:
            common_logger.error(f"[ComfyUI] Error getting result from ComfyUI: {e}")
            return []
