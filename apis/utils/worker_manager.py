import json

import redis
from configs.celery_conf import broker_url
from apis.models.remote_host import RemoteHost
from tools.logger import common_logger


class WorkerManager:
    def __init__(self):
        conn = redis.Redis.from_url(broker_url)
        self.__conn = conn

    def add_update_worker(self, remote_host: RemoteHost) -> dict:
        try:
            res = self.__conn.hset("workers", remote_host.host_name, remote_host.model_dump_json())
            common_logger.info(f"[Common] 添加/更新主机 {remote_host.host_name} 成功，结果为：{res}")
            return {"host": remote_host.model_dump(), "result": True}
        except Exception as e:
            common_logger.error(f"[Common] 添加/更新主机 {remote_host.host_name} 失败，错误信息为：{e}")
            return {"host": remote_host.model_dump(), "result": False}

    def get_workers(self, host_name: str = "all") -> list[dict]:
        if host_name != "all":
            res = self.__conn.hget("workers", host_name)
            if res is None:
                return []
            return [json.loads(self.__conn.hget("workers", host_name).decode())]
        hosts = []
        res = self.__conn.hgetall("workers")
        for k, v in res.items():
            hosts.append(json.loads(v.decode()))
        return hosts

    def remove_worker(self, host_name: str) -> bool:
        try:
            self.__conn.hdel("workers", host_name)
            return True
        except Exception as e:
            common_logger.error(f"[Common] 删除主机 {host_name} 失败，错误信息为：{e}")
            return False

manager = WorkerManager()
