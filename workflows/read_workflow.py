import json
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from apis.models.remote_host import RemoteHost
from apis.models.settings import OssSetting
from apis.utils.pre_process import PreProcess
from tools.execute import Execute
from tools.logger import common_logger
from tools.utils import get_host_status
from workflows.fooocus.map_rule import fooocus_mapping
from workflows.fooocus.mapping import mapped_workflow, post_mapped_fooocus


class Workflow:
    """
    workflow
    """
    def __init__(
            self,
            params: object,
            task_type: str,
            oss_conf: OssSetting,
            exec_hosts: list[RemoteHost]
        ):
        """
        初始化一个工作流对象
        :param params: 请求参数对象
        :param task_type: 任务类型，用来选择要执行的工作流, fooocus
        :param oss_conf: Oss 客户端配置
        :param exec_hosts: 符合条件的主机列表
        """
        cur_dir = os.path.dirname(__file__)
        self.__pre_process = PreProcess(oss_conf)
        self.params = params
        self.task_type = task_type
        self.exec_hosts = exec_hosts
        try:
            with open(os.path.join(cur_dir, f"{task_type}.json"), "r") as f:
                self.flow = json.load(f)
        except Exception as e:
            common_logger.error(f"[Execute] 读取工作流 {task_type}.json 文件失败，错误信息为：{e}")
            self.flow = {}

    def __parse_param(self) -> dict:
        """
        把参数解析到 workflow 中
        :return:
        """
        parsed_params, image_map_list = self.__pre_process.pre_process(self.params)
        parsed_params["image_number"] = 1
        if self.task_type == "fooocus":
            workflow = post_mapped_fooocus(mapped_workflow(self.flow, parsed_params, fooocus_mapping))
        else:
            # todo: 添加其他任务类型的工作流
            workflow = self.flow

        return {
            "workflow": workflow,
            "image_map_list": image_map_list,
            "image_number": parsed_params.get("image_number"),
        }

    def __get_exec_hosts(self) -> RemoteHost:
        """
        选择合适的主机
        :return:
        """
        exec_host = get_host_status(self.exec_hosts)
        return min(exec_host, key=lambda x: x.queue.get("queue_pending"))


    def run_task(self):
        parsed_param = self.__parse_param()
        workflow = parsed_param.get("workflow")
        image_map_list = parsed_param.get("image_map_list")
        image_number = parsed_param.get("image_number")
        tasks = [workflow.copy() for _ in range(image_number)]


        max_retries = 3
        def execute_task_with_retry(task, retries=0):
            """
            执行单个任务并支持重试
            :param task: 任务对象
            :param retries: 当前重试次数
            :return: 执行结果
            """
            try:
                execute = Execute(server_address=self.__get_exec_hosts().host_ip)
                execute.execute(task)
                return {"status": "success", "message": "任务执行成功"}
            except Exception as e:
                if retries < max_retries:
                    common_logger.warning(f"[Execute] 任务失败，正在重试 ({retries + 1}/{max_retries})，错误信息为：{e}")
                    return execute_task_with_retry(task, retries + 1)
                common_logger.error(f"[Execute] 任务最终失败，错误信息为：{e}")
                return {"status": "error", "message": str(e)}

        try:
            with ThreadPoolExecutor(max_workers=image_number) as executor:
                wrapped_execute_task = partial(execute_task_with_retry, retries=0)
                futures = [executor.submit(wrapped_execute_task, task) for task in tasks]
                results = [future.result() for future in futures]
        except Exception as pool_exception:
            common_logger.error(f"[Execute] 线程池执行异常：{pool_exception}")
            return {"status": "error", "message": "线程池执行失败", "results": []}

        self.__pre_process.clean_memory(image_map_list)

        if any(result.get("status") == "error" for result in results):
            return {
                "status": "error",
                "message": "部分任务执行失败",
                "results": results
            }

        return {
            "status": "success",
            "message": "所有任务执行成功",
            "results": results
        }
