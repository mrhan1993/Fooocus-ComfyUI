"""OSS客户端
class:
    AliyunOssClient: 阿里云OSS客户端
    QcloudOssClient: 腾讯云OSS客户端
    OssClient: 通过该类可以自动选择对应的OSS客户端
"""
from tools.store.aliyun import AliyunOssClient
from tools.store.qcloud import QcloudOssClient


class OssClient:
    SUPPORTED_SERVICES = {
        'aliyun': AliyunOssClient,
        'qcloud': QcloudOssClient
    }

    def __init__(self, service: str, config: dict) -> None:
        """初始化OSS客户端
        :param service: 服务提供商，如 aliyun, qcloud, qiniu, s3, google
        :param config: 配置文件，应该包含各个服务商的配置信息，根据服务商不同，配置信息不同
        """
        if service not in self.SUPPORTED_SERVICES:
            raise ValueError(f"Unsupported service: {service}")

        self.__client = self.SUPPORTED_SERVICES[service](config)

    @property
    def client(self):
        return self.__client

    def upload_file(self, file_path: str | bytes, object_name: str) -> bool:
        """上传文件
        :param file_path: 本地文件路径
        :param object_name: 对象名称，即文件名，远程文件路径
        :return: bool
        """
        return self.client.upload_file(file_path, object_name)

    def delete_file(self, object_name: str) -> bool:
        """删除文件
        :param object_name: 对象名称，即文件名，远程文件路径
        :return: bool or str
        """
        return self.client.delete_file(object_name)

    def get_file(self, object_name: str) -> str:
        """获取文件url, 返回文件地址或者 False
        :param object_name: 对象名称，即文件名，远程文件路径
        :return: bool or str
        """
        return self.client.get_file(object_name)
