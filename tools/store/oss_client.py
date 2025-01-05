"""OSS客户端
class:
    AliyunOssClient: 阿里云OSS客户端
    QcloudOssClient: 腾讯云OSS客户端
    OssClient: 通过该类可以自动选择对应的OSS客户端
"""
from tools.store.aliyun import AliyunOssClient
from tools.store.qcloud import QcloudOssClient
from tools.logger import common_logger
from apis.models.settings import OssSetting


class OssClient:
    SUPPORTED_SERVICES = {
        'aliyun': AliyunOssClient,
        'qcloud': QcloudOssClient
    }

    def __init__(self, config: OssSetting) -> None:
        """初始化OSS客户端
        :param config: 配置文件，应该包含各个服务商的配置信息，根据服务商不同，配置信息不同
        """
        if config.choice.value not in self.SUPPORTED_SERVICES:
            raise ValueError(f"Unsupported service: {config.choice.value}")

        try:
            self.__client = self.SUPPORTED_SERVICES[config.choice.value](config)
            common_logger.info(f"[OSS] 初始化 {config.choice.value} OSS 客户端成功")
        except Exception as e:
            common_logger.error(f"[OSS] 初始化 {config.choice.value} OSS 客户端失败: {e}")

    @property
    def client(self):
        return self.__client

    def upload_file(self, file_path: str | bytes, object_name: str) -> bool:
        """上传文件
        :param file_path: 本地文件路径
        :param object_name: 对象名称，即文件名，远程文件路径
        :return: bool
        """
        try:
            return self.client.upload_file(file_path, object_name)
        except Exception as e:
            common_logger.error(f"[OSS] 上传文件失败: {e}")
            return False

    def delete_file(self, object_name: str) -> bool:
        """删除文件
        :param object_name: 对象名称，即文件名，远程文件路径
        :return: bool or str
        """
        try:
            return self.client.delete_file(object_name)
        except Exception as e:
            common_logger.error(f"[OSS] 删除文件失败: {e}")
            return False

    def get_file(self, object_name: str) -> str:
        """获取文件url, 返回文件地址或者 False
        :param object_name: 对象名称，即文件名，远程文件路径
        :return: bool or str
        """
        try:
            return self.client.get_file(object_name)
        except Exception as e:
            common_logger.error(f"[OSS] 获取文件地址失败: {e}")
            return ""
