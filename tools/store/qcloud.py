"""腾讯云 OSS 客户端"""
from qcloud_cos import CosConfig, CosS3Client
from tools.logger import common_logger


class QcloudOssClient:
    def __init__(self, config: dict) -> None:
        """初始化腾讯云OSS客户端
        :param config: 配置文件，应该包含以下字段
            access_key_id: 腾讯云的secret_id
            access_key_secret: 腾讯云的secret_key
            bucket: OSS的bucket名称
            region: OSS的区域，如 ap-shanghai
        """
        required_keys = ['access_key_id', 'access_key_secret', 'bucket', 'region']
        for key in required_keys:
            if key not in config:
                common_logger.error(f"[QCloud OSS] Missing required key: {key}")
                raise ValueError(f"Missing required key: {key}")
        self.__bucket = config['bucket']
        ak_id = config['access_key_id']
        ak_secret = config['access_key_secret']
        region = config['region']
        config = CosConfig(Region=region, SecretId=ak_id, SecretKey=ak_secret)
        self.__client = CosS3Client(config)

    def upload_file(self, file_path: str | bytes, object_name: str) -> bool:
        """上传文件
        :param file_path: 文件路径或 bytes
        :param object_name: 对象名称，即文件名
        """
        if isinstance(file_path, bytes):
            try:
                self.__client.put_object(
                    Bucket=self.__bucket,
                    Body=file_path,
                    Key=object_name
                )
                return True
            except Exception as e:
                common_logger.error(f"[QCloud OSS] Failed to upload file: {e}")
                return False
        try:
            self.__client.upload_file(
                Bucket=self.__bucket,
                LocalFilePath=file_path,
                Key=object_name
            )
            return True
        except Exception as e:
            common_logger.error(f"[QCloud OSS] Failed to upload file: {e}")
            return False

    def delete_file(self, object_name: str) -> bool:
        """删除文件
        :param object_name: 对象名称，即文件名
        """
        try:
            self.__client.delete_object(
                Bucket=self.__bucket,
                Key=object_name
            )
            return True
        except Exception as e:
            return False

    def get_file(self, object_name: str) -> str:
        """获取文件url
        :param object_name: 对象名称，即文件名
        """
        try:
            return self.__client.get_presigned_url(
                Method="GET",
                Bucket=self.__bucket,
                Key=object_name,
                Expired=3600
            )
        except Exception as e:
            return ""
