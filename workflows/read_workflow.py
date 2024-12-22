import json
import os

from tools.logger import common_logger


class Workflow:
    """
    workflow
    """
    def __init__(
            self,
            name: str,
            params: dict,
            vram_weight: float = 1.0,
            flop_weight: float = 1.0,
            queue_weight: float = 1.0,
            node_select: str = "default",
        ):
        """
        初始化一个工作流对象
        :param name: 工作流文件名
        :param params: 请求参数
        :param vram_weight: 显存需求权重
        :param flop_weight: 算力需求权重
        :param queue_weight: 队列需求
        :param node_select: 指定节点
        """
        cur_dir = os.path.dirname(__file__)
        self.params = params
        self.vram_weight = vram_weight
        self.flop_weight = flop_weight
        self.node_select = node_select
        try:
            self.value = json.load(open(os.path.join(cur_dir, f"{name}.json"), "r"))
        except Exception as e:
            common_logger.error(f"[Common] 读取工作流 {name}.json 文件失败，错误信息为：{e}")
            self.value = {}

    def __parse_param(self) -> dict:
        """
        把参数解析到 workflow 中
        :return:
        """
        pass

    def run_task(self):
        pass
