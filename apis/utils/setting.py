import json
import re

import redis

from apis.models.settings import Settings, TransList
from configs.celery_conf import broker_url
from tools.llm_client.llm_client import LlmClient
from tools.logger import common_logger
from tools.store.oss_client import OssClient
from tools.translate.trans_client import TranslateClient


class SettingManager:
    def __init__(self):
        self.__conn = redis.Redis.from_url(broker_url)

    def add_update_setting(self, setting: Settings) -> bool:
        try:
            self.__conn.hset("settings", setting.id, setting.model_dump_json())
            common_logger.info(f"[common] Add or update settings success")
            return True
        except Exception as e:
            common_logger.error(f"[common] Add or update settings failed, message: {e}")
            return False

    def get_setting(self, setting_id: str) -> Settings | None:
        setting = self.__conn.hget("settings", setting_id)
        if setting:
            return Settings(**json.loads(setting))
        else:
            return None

    def validate_setting(self) -> dict:
        """
        Validate setting
        :return: {"oss": True, "llm": True, "translation": True}
        """
        result = {
            "oss": True,
            "llm": True,
            "translation": True
        }
        default = self.get_setting("default")

        if not default:
            common_logger.error("[common] Validate setting failed, default setting not found")
            return {"oss": False, "llm": False, "translation": False}

        oss = OssClient(default.oss)
        if not oss.upload_file("./ThisImageForValidateSetting", "ThisImageForValidateSetting"):
            common_logger.error("[common] Validate setting failed, oss upload failed")
            result["oss"] = False

        if default.translation.enabled and default.translation.choice != TransList.llm:
            trans = TranslateClient(default.translation)
            if trans.translate("今天").lower() != "today":
                common_logger.error("[common] Validate setting failed, translation failed")
                result["translation"] = False

        if default.llm.enabled:
            llm = LlmClient(default.llm)
            if len(re.findall("today", llm.translate("今天").lower())) == 0:
                common_logger.error("[common] Validate setting failed, llm translate failed")
                result["llm"] = False

        if default.translation.enabled and default.translation.choice == TransList.llm and not default.llm.enabled:
            common_logger.error("[common] Validate setting failed, llm is not enabled")
            result["llm"] = False

        return result


setting_manager = SettingManager()
