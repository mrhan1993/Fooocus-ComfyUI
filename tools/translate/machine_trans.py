import json
import requests
import random
from hashlib import md5
import nltk
from nltk.corpus import words

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import tmt_client, models

from typing import List

from alibabacloud_alimt20181012.client import Client as alimt20181012Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alimt20181012 import models as alimt_20181012_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

from tools.logger import common_logger


def is_english(text: str) -> bool:
    """
    Check if a given string is English.
    :param text: The string to check.
    :return: True if the string is English, False otherwise.
    """
    english_words = set(words.words())
    words_in_text = text.split()
    english_word_count = sum(1 for word in words_in_text if word.lower() in english_words)
    return english_word_count / len(words_in_text) >= 0.85

class TencentTranslateClient:
    def __init__(self, config: dict = None):
        """
        使用AK&SK初始化账号Client
        @param config: 公共配置
        @throws Exception
        """
        required_keys = ['access_key_id', 'access_key_secret', 'endpoint', 'region']
        for key in required_keys:
            if key not in config:
                common_logger.error(f"[TencentTranslate] Missing required key: {key}")
                raise ValueError(f"Missing required key: {key}")
        secret_id = config.get('access_key_id')
        secret_key = config.get('access_key_secret')
        end_point = config.get('endpoint')
        region = config.get('region')

        cred = credential.Credential(secret_id, secret_key)
        http_profile = HttpProfile()
        http_profile.endpoint = end_point

        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        self.__client = tmt_client.TmtClient(cred, region, client_profile)

    def trans(self, text: str) -> str:
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
        except Exception as e:
            common_logger.error(f"[TencentTranslate] Failed to translate: {e}")
            return text
        result = json.loads(resp.to_json_string())["TargetText"]
        return result.lower()


class AliTranslateClient:
    def __init__(self, config: dict = None):
        """
        使用 AK&SK 初始化账号 Client
        @param config: 公共配置
        @throws Exception
        Endpoint 请参考 https://api.aliyun.com/product/alimt
        """
        trans_config = open_api_models.Config(
            access_key_id=config.get('access_key_id'),
            access_key_secret=config.get('access_key_secret')
        )
        trans_config.endpoint = config.get('endpoint')
        self.__client = alimt20181012Client(trans_config)

    def trans(self, text: str) -> str:
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
    def __init__(self, config: dict = None):
        self.__app_id = config.get("app_id")
        self.__app_key = config.get("app_key")

        self.__url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'

    def trans(self, text: str) -> str:
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
            r = requests.post(self.__url, params=payload, headers=headers)
            result = r.json()
            return result['trans_result'][0]['dst'].lower().strip()
        except Exception as e:
            common_logger.error(f"[BaiduTranslate] Failed to translate: {e}")
            return text
