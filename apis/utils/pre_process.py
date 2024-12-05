import uuid
import base64
from datetime import datetime
from typing import Any

from tools.utils import GlobalMemory
from apis.utils.img_utils import (
    base64_to_bytesimg,
    get_ext_from_bytes
)
from tools.store.oss_client import OssClient
from configs.store_conf import (
    service_type,
    store_config
)


memory = GlobalMemory()
client = OssClient(service_type, store_config)


def pre_process(params: Any) -> Any:
    """
    Pre-process the parameters. Upload image and replace to remote obj name
    遍历字典，并将其中的 base64 图像上传到 oss，上传成功后将 base64 存储到一个全局
    对象，
    :param params: The parameters to pre-process.
    :return: The pre-processed parameters.
    """
    image_map_list = []
    if isinstance(params, dict):
        for key, value in params.items():
            params[key] = pre_process(value)
        params['image_map_list'] = image_map_list
        return params
    elif isinstance(params, list):
        return [pre_process(item) for item in params]
    elif isinstance(params, str):
        try:
            # 尝试解码 base64 字符串
            decoded_bytes = base64_to_bytesimg(params)
            ext = get_ext_from_bytes(decoded_bytes)
            today = datetime.now().strftime("%Y%m%d")
            remote_file_name = uuid.uuid4().hex
            remote_path = f"{today}/{remote_file_name}.{ext}"
            # 上传文件到 oss
            res = client.upload_file(decoded_bytes, remote_path)
            if res:
                memory.set(remote_file_name, params)
                image_map_list.append(remote_file_name)
                return remote_path
            return None
        except Exception:
            # 如果不是有效的 base64 字符串，保持原样
            return params
    else:
        return params


def clean_memory(clean_list: list) -> None:
    """
    Clean up the memory.
    """
    for item in clean_list:
        memory.delete(item)
