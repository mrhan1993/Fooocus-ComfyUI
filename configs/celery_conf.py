"""
Config for project.
由于 Redis 额外用作后端信息存储，因此如果使用 MQ 的话，需要将 worker_manager 中的配置引入进行修改
"""
# [Celery]
# celery 配置文件 https://docs.celeryq.dev/en/stable/userguide/configuration.html
broker_url = 'redis://:86WCqsULA2UuwZg@10.0.0.125:6379/0'
result_backend = 'db+mysql://root:86WCqsULA2UuwZg@10.0.0.125:3306/celery_results'

task_serializer = 'json'
result_serializer = 'json'
result_expires = 0
accept_content = ['json']
timezone = 'Asia/Shanghai'
enable_utc = False
worker_concurrency = 2
broker_connection_retry_on_startup = True
redis_backend_health_check_interval = 5
redis_socket_keepalive = True

task_track_started = True
database_short_lived_sessions = True
