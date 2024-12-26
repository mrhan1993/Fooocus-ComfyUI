"""阿里云 OSS 客户端"""
import oss2
from apis.models.settings import OssSetting
from tools.logger import common_logger


class AliyunOssClient:
    def __init__(self, config: OssSetting) -> None:
        """初始化阿里云OSS客户端
        :param config: 配置文件，应该包含以下字段
            endpoint: OSS的endpoint，如 oss-cn-beijing.aliyuncs.com
            access_key_id: 阿里云的access_key_id
            access_key_secret: 阿里云的access_key_secret
            bucket: OSS的bucket名称
            region: OSS的区域，如 cn-beijing
        """
        self.__config = config
        try:
            auth = oss2.Auth(config.access_key_id, config.access_key_secret)
            self.__bucket = oss2.Bucket(
                auth=auth,
                endpoint=config.endpoint,
                bucket_name=config.bucket,
                region=config.region
            )
            common_logger.info(f"[AliyunOss] init success")
        except Exception as e:
            common_logger.error(f"[AliyunOss] init failed: {e}")

    def upload_file(self, file_path: str | bytes, object_name: str) -> bool:
        """上传文件
        :param file_path: 本地文件路径或 bytes
        :param object_name: 对象名称，即文件名，远程文件路径
        """
        if isinstance(file_path, bytes):
            try:
                self.__bucket.put_object(object_name, file_path)
                return True
            except Exception as e:
                common_logger.error(f"[AliyunOss] upload file failed: {e}")
                return False
        try:
            self.__bucket.put_object_from_file(object_name, file_path)
            return True
        except Exception as e:
            common_logger.error(f"[AliyunOss] upload file failed: {e}")
            return False

    def delete_file(self, object_name: str) -> bool:
        """删除文件
        :param object_name: 对象名称，即文件名，远程文件路径
        """
        try:
            self.__bucket.delete_object(object_name)
            return True
        except Exception as e:
            common_logger.error(f"[AliyunOss] delete file failed: {e}")
            return False

    def get_file(self, object_name: str) -> str:
        """获取文件url
        :param object_name: 对象名称，即文件名，远程文件路径
        """
        try:
            return self.__bucket.sign_url('GET', object_name, 3600, slash_safe=True)
        except Exception as e:
            common_logger.error(f"[AliyunOss] get file url failed: {e}")
            return ""
