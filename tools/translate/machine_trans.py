import json
import random
from hashlib import md5

import requests
from alibabacloud_alimt20181012 import models as alimt_20181012_models
from alibabacloud_alimt20181012.client import Client as alimt20181012Client
from alibabacloud_tea_openapi import models as open_api_models
from langdetect import detect
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import tmt_client, models

from apis.models.settings import TransSetting
from tools.logger import common_logger


def is_english(text: str) -> bool:
    """
    Check if a given string is English.
    :param text: The string to check.
    :return: True if the string is English, False otherwise.
    """
    try:
        return detect(text) == 'en'
    except Exception:
        return False

class TencentTranslateClient:
    def __init__(self, config: TransSetting):
        """
        使用AK&SK初始化账号Client
        @param config: 公共配置
        @throws Exception
        """
        try:
            cred = credential.Credential(config.access_key_id, config.access_key_secret)
            http_profile = HttpProfile()
            http_profile.endpoint = config.endpoint

            client_profile = ClientProfile()
            client_profile.httpProfile = http_profile
            self.__client = tmt_client.TmtClient(cred, config.region, client_profile)
        except Exception as e:
            common_logger.error(f"[TencentTranslate] Failed to init client: {e}")
            self.__client = None

    def translate(self, text: str) -> str:
        if is_english(text):
            return text
        req = models.TextTranslateRequest()
        params = {
            "SourceText": text,
            "Source": "auto",
            "Target": "en",
            "ProjectId": 0
        }
        req.from_json_string(json.dumps(params))
        try:
            resp = self.__client.TextTranslate(req)
            result = json.loads(resp.to_json_string())["TargetText"]
        except Exception as e:
            common_logger.error(f"[TencentTranslate] Failed to translate: {e}")
            return text
        return result.lower()


class AliTranslateClient:
    def __init__(self, config: TransSetting):
        """
        使用 AK&SK 初始化账号 Client
        @param config: 公共配置
        @throws Exception
        Endpoint 请参考 https://api.aliyun.com/product/alimt
        """
        try:
            trans_config = open_api_models.Config(
                access_key_id=config.access_key_id,
                access_key_secret=config.access_key_secret
            )
            trans_config.endpoint = config.endpoint
            self.__client = alimt20181012Client(trans_config)
        except Exception as e:
            common_logger.error(f"[AliTranslate] Failed to init client: {e}")

    def translate(self, text: str) -> str:
        request = alimt_20181012_models.TranslateGeneralRequest(
            format_type='text',
            source_language='auto',
            target_language='en',
            source_text=text,
            scene='general'
        )
        try:
            response = self.__client.translate_general(request)
        except Exception as e:
            common_logger.error(f"[AliTranslate] Failed to translate: {e}")
            return text
        return response.body.data.translated


class BaiduTranslateClient:
    def __init__(self, config: TransSetting):
        self.__app_id = config.access_key_id
        self.__app_key = config.access_key_secret

        self.__url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'

    def translate(self, text: str) -> str:
        """
        Translate text using Baidu Translate API
        :param text: Text to translate
        :return: Translated text
        """
        def make_md5(s, encoding='utf-8'):
            return md5(s.encode(encoding)).hexdigest()

        salt = random.randint(32768, 65536)
        sign = make_md5(self.__app_id + text + str(salt) + self.__app_key)

        # Build request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': self.__app_id, 'q': text, 'from': 'auto', 'to': 'en', 'salt': salt, 'sign': sign}

        # Send request
        try:
            r = requests.post(self.__url, params=payload, headers=headers, timeout=30)
            result = r.json()
            return result['trans_result'][0]['dst'].lower().strip()
        except Exception as e:
            common_logger.error(f"[BaiduTranslate] Failed to translate: {e}")
            return text
