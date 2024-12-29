import uuid
from datetime import datetime
from typing import Any

from apis.models.settings import OssSetting
from tools.utils import GlobalMemory
from apis.utils.img_utils import (
    base64_to_bytesimg,
    get_ext_from_bytes
)
from tools.store.oss_client import OssClient


memory = GlobalMemory()


class PreProcess:
    def __init__(self, oss_config: OssSetting):
        self.__memory = memory
        self.__oss = OssClient(oss_config)

    def translate(self, params: Any) -> Any:
        """
        Pre-process the parameters.
        :param params: The parameters to pre-process.
        :return: The pre-processed parameters
        """
        # todo: 翻译提示词
        return params

    def optimize_prompt(self, params: Any) -> Any:
        """
        Optimize prompts
        :param params:
        :return:
        """
        # todo: 优化提示词
        return params

    def upload_images(self, params: Any) -> Any:
        """
        Pre-process the parameters. Upload image and replace to remote obj name
        遍历字典，并将其中的 base64 图像上传到 oss，上传成功后将 base64 存储到一个全局
        对象，
        :param params: The parameters to pre-process.
        :return: The pre-processed parameters and uploaded image list name
        """
        image_map_list = []
        if isinstance(params, dict):
            for key, value in params.items():
                params[key] = self.upload_images(value)
            params['image_map_list'] = image_map_list
            return params
        elif isinstance(params, list):
            return [self.upload_images(item) for item in params]
        elif isinstance(params, str):
            try:
                # 尝试解码 base64 字符串
                decoded_bytes = base64_to_bytesimg(params)
                ext = get_ext_from_bytes(decoded_bytes)
                today = datetime.now().strftime("%Y%m%d")
                remote_file_name = uuid.uuid4().hex
                remote_path = f"{today}/{remote_file_name}.{ext}"
                # 上传文件到 oss
                res = self.__oss.upload_file(decoded_bytes, remote_path)
                if res:
                    memory.set(remote_file_name, params)
                    image_map_list.append(remote_file_name)
                    return remote_path
                return None
            except Exception:
                # 如果不是有效的 base64 字符串，保持原样
                return params
        else:
            return params, image_map_list

    def pre_process(self, params: Any):
        """
        Pre-process the parameters.
        :param params: The parameters to pre-process.
        :return: The pre-processed parameters and image map list
        """
        uploaded_params, image_map_list = self.upload_images(params)
        return self.optimize_prompt(
            self.translate(uploaded_params)), image_map_list

    def clean_memory(self, clean_list: list) -> None:
        """
        Clean up the memory.
        """
        for item in clean_list:
            self.__memory.delete(item)
