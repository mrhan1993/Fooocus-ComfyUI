import json
import redis

from apis.models.settings import Settings
from configs.celery_conf import broker_url
from tools.logger import common_logger


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

    def get_setting(self, setting_id: str) -> Settings:
        setting = self.__conn.hget("settings", setting_id)
        if setting:
            return Settings(**json.loads(setting))
        else:
            return Settings()

setting_manager = SettingManager()
