"""Translate 客户端
class:
    TencentTranslateClient: 阿里云OSS客户端
    AliTranslateClient: 腾讯云OSS客户端
    BaiduTranslateClient: 通过该类可以自动选择对应的OSS客户端
"""
from tools.translate.machine_trans import (
    TencentTranslateClient,
    AliTranslateClient,
    BaiduTranslateClient
)
from tools.llm_client.llm_client import LlmClient
from tools.logger import common_logger
from apis.models.settings import TransSetting, LlmSetting


class TranslateClient:
    SUPPORTED_SERVICES = {
        'aliyun': AliTranslateClient,
        'qcloud': TencentTranslateClient,
        'baidu': BaiduTranslateClient,
        'llm': LlmClient
    }

    def __init__(self, config: TransSetting | LlmSetting) -> None:
        self.__config = config
        if isinstance(config, TransSetting):
            self.__client = self.SUPPORTED_SERVICES[config.choice.value](config)
        else:
            self.__client = LlmClient(config)

    def translate(self, text: str) -> str:
        """翻译
        Args:
            text (str): 待翻译文本
        Returns:
            str: 翻译结果
        """
        try:
            return self.__client.translate(text)
        except Exception as e:
            common_logger.error(f"[Translate] translate failed, error: {e}, service: {self.__config.choice.value}")
            return text
