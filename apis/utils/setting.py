import json
import os.path
import re

import redis

from apis.models.settings import Settings, TransList
from configs.celery_conf import broker_url
from tools.llm_client.llm_client import LlmClient
from tools.logger import common_logger
from tools.store.oss_client import OssClient
from tools.translate.trans_client import TranslateClient


class SettingManager:
    """
    Setting manager
    Functions:
        - add_update_setting
        - get_setting
        - validate_setting
    """
    def __init__(self):
        self.__conn = redis.Redis.from_url(broker_url)

    def add_update_setting(self, setting: Settings) -> dict:
        """
        Add or update setting
        :param setting: Settings object
        :return: {"result": True, "detail": valid}
        """
        valid = self.validate_setting(setting)
        try:
            if not valid["oss"] or not valid["llm"] or not valid["translation"]:
                common_logger.error(f"[common] Add or update settings failed, {valid}")
                return {"result": False, "detail": valid}
            self.__conn.hset("settings", setting.id, setting.model_dump_json())
            common_logger.info(f"[common] Add or update settings success")
            return {"result": True, "detail": valid}
        except Exception as e:
            common_logger.error(f"[common] Add or update settings failed, message: {e}")
            return {"result": False, "detail": valid}

    def get_setting(self, setting_id: str) -> Settings | None:
        """
        Get setting by setting_id
        :param setting_id:
        :return:
        """
        setting = self.__conn.hget("settings", setting_id)
        if setting:
            return Settings(**json.loads(setting))
        else:
            return None

    @staticmethod
    def validate_setting(setting: Settings) -> dict:
        """
        Validate setting
        :return: {"oss": True, "llm": True, "translation": True}
        """
        result = {
            "oss": True,
            "llm": True,
            "translation": True
        }

        if not setting:
            common_logger.error("[common] Validate setting failed, default setting not found")
            return {"oss": False, "llm": False, "translation": False}

        try:
            oss = OssClient(setting.oss)
            current_dir = os.path.dirname(__file__)
            with open(os.path.join(current_dir, "./ThisImageForValidateSetting.png"), "rb") as f:
                valid_image = f.read()
            if not oss.upload_file(valid_image, "ThisImageForValidateSetting"):
                common_logger.error("[common] Validate setting failed, oss upload failed")
                result["oss"] = False
        except Exception as e:
            common_logger.error(f"[common] Validate setting failed, oss upload failed, message: {e}")
            result["oss"] = False

        if setting.translation.enabled and setting.translation.choice != TransList.llm:
            try:
                trans = TranslateClient(setting.translation)
                if trans.translate("今天").lower() != "today":
                    common_logger.error("[common] Validate setting failed, translation failed")
                    result["translation"] = False
            except Exception as e:
                common_logger.error(f"[common] Validate setting failed, translation failed, message: {e}")

        if setting.llm.enabled:
            try:
                llm = LlmClient(setting.llm)
                if len(re.findall("today", llm.translate("今天").lower())) == 0:
                    common_logger.error("[common] Validate setting failed, llm Validate failed")
                    result["llm"] = False
            except Exception as e:
                common_logger.error(f"[common] Validate setting failed, llm Validate failed, message: {e}")
                result["llm"] = False
        try:
            if setting.translation.enabled and setting.translation.choice == TransList.llm and not setting.llm.enabled:
                common_logger.error("[common] Validate llm translate setting failed, llm must enabled when translation is llm")
                result["llm"] = False
        except Exception as e:
            common_logger.error(f"[common] Validate llm translate setting failed, llm Validate failed, message: {e}")
            result["llm"] = False

        return result


setting_manager = SettingManager()
