import uuid
from datetime import datetime
from io import BytesIO
from typing import Any

from PIL import Image

from apis.models.settings import OssSetting, Settings
from tools.utils import GlobalMemory
from apis.utils.img_utils import (
    base64_to_bytesimg,
    get_ext_from_bytes
)
from tools.store.oss_client import OssClient


memory = GlobalMemory()


class PreProcess:
    def __init__(self, setting: Settings):
        self.__setting = setting
        self.__memory = memory
        self.__oss = OssClient(self.__setting.oss)

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

    def upload_images(self, params: Any, image_map_list: list) -> Any:
        """
        Pre-process the parameters. Upload image and replace to remote obj name
        遍历字典，并将其中的 base64 图像上传到 oss，上传成功后将 base64 存储到一个全局
        对象，
        :param params: The parameters to pre-process.
        :param image_map_list: List to store uploaded image names.
        :return: The pre-processed parameters and uploaded image list name
        """
        if isinstance(params, dict):
            for key, value in params.items():
                processed_value, image_map_list = self.upload_images(value, image_map_list)
                params[key] = processed_value
            params['image_map_list'] = image_map_list
            return params, image_map_list
        elif isinstance(params, list):
            processed_list = []
            for item in params:
                processed_item, image_map_list = self.upload_images(item, image_map_list)
                processed_list.append(processed_item)
            return processed_list, image_map_list
        elif isinstance(params, str):
            try:
                # 尝试解码 base64 字符串
                decoded_bytes = base64_to_bytesimg(params)
                try:
                    buffer = BytesIO(decoded_bytes)
                    Image.open(buffer)
                except Exception:
                    return params, image_map_list
                ext = get_ext_from_bytes(decoded_bytes)
                today = datetime.now().strftime("%Y%m%d")
                remote_file_name = uuid.uuid4().hex
                remote_path = f"inputs/{today}/{remote_file_name}.{ext}"
                # 上传文件到 oss
                res = self.__oss.upload_file(decoded_bytes, remote_path)
                if res:
                    memory.set(remote_file_name, params)
                    image_map_list.append(remote_file_name)
                    return remote_path, image_map_list
                return None, image_map_list
            except Exception:
                # 如果不是有效的 base64 字符串，保持原样
                return params, image_map_list
        else:
            return params, image_map_list

    def pre_process(self, params: Any):
        """
        Pre-process the parameters.
        :param params: The parameters to pre-process.
        :return: The pre-processed parameters and image map list
        """
        uploaded_params, image_map_list = self.upload_images(params.model_dump(), [])
        return self.optimize_prompt(
            self.translate(uploaded_params)), image_map_list

    def clean_memory(self, clean_list: list) -> None:
        """
        Clean up the memory.
        """
        for item in clean_list:
            self.__memory.delete(item)
