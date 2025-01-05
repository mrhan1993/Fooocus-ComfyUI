import json

import redis

from apis.models.remote_host import RemoteHostsDB, RemoteHostDB
from configs.celery_conf import broker_url
from tools.logger import common_logger


class WorkerManager:
    def __init__(self):
        self.__conn = redis.Redis.from_url(broker_url)

    def add_update_worker(self, remote_host: RemoteHostDB) -> dict:
        """
        Add or update worker.
        :param remote_host: RemoteHost object
        :return: {"host": RemoteHost, "result": True} or {"host": RemoteHost, "result": False}
        """
        try:
            res = self.__conn.hset("workers", remote_host.host_name, remote_host.model_dump_json())
            common_logger.info(f"[Common] 添加/更新主机 {remote_host.host_name} 成功，结果为：{res}")
            return {"host": remote_host.model_dump(), "result": True}
        except Exception as e:
            common_logger.error(f"[Common] 添加/更新主机 {remote_host.host_name} 失败，错误信息为：{e}")
            return {"host": remote_host.model_dump(), "result": False}

    def get_workers(self, host_name: str = "all") -> RemoteHostsDB:
        """
        Get worker.
        :param host_name: Get host for given name, 'all' for all
        :return: A list of workers.
        """
        if host_name != "all":
            res = self.__conn.hget("workers", host_name)
            if res is None:
                return RemoteHostsDB(hosts=[])
            host = json.loads(self.__conn.hget("workers", host_name).decode())
            RemoteHostDB(**host)
            return RemoteHostsDB(hosts=[host])
        hosts = []
        res = self.__conn.hgetall("workers")
        for _, v in res.items():
            hosts.append(json.loads(v.decode()))
        return RemoteHostsDB(**{"hosts": hosts})

    def remove_worker(self, host_name: str) -> bool:
        """
        Remove worker by name, if not exist, return True
        :param host_name: host_name
        :return: True or False
        """
        try:
            self.__conn.hdel("workers", host_name)
            common_logger.info(f"[Common] 删除主机 {host_name} 成功")
            return True
        except Exception as e:
            common_logger.error(f"[Common] 删除主机 {host_name} 失败，错误信息为：{e}")
            return False

manager = WorkerManager()
