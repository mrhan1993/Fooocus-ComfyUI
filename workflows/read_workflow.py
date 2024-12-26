import json
import os

from apis.models.remote_host import RemoteHost
from tools.logger import common_logger
from tools.utils import get_host_status
from apis.utils.pre_process import PreProcess


class Workflow:
    """
    workflow
    """
    def __init__(
            self,
            params: object,
            task_type: str,
            exec_hosts: list[RemoteHost]
        ):
        """
        初始化一个工作流对象
        :param params: 请求参数对象
        :param task_type: 任务类型，用来选择要执行的工作流
        :param exec_hosts: 符合条件的主机列表
        """
        cur_dir = os.path.dirname(__file__)
        self.__pre_process = PreProcess()
        self.params = params
        self.task_type = task_type
        self.exec_hosts = get_host_status(exec_hosts)
        try:
            self.flow = json.load(open(os.path.join(cur_dir, f"{task_type}.json"), "r"))
        except Exception as e:
            common_logger.error(f"[Common] 读取工作流 {task_type}.json 文件失败，错误信息为：{e}")
            self.flow = {}

    def __parse_param(self) -> dict:
        """
        把参数解析到 workflow 中
        :return:
        """
        parsed_params, image_map_list = self.__pre_process.pre_process(self.params)

        return {
            "params": parsed_params,
            "image_map_list": image_map_list
        }


    def run_task(self):
        processed_params = self.__parse_param()
        self.__pre_process.clean_memory(processed_params["image_map_list"])
