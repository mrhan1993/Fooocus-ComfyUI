import platform
import subprocess
import uvicorn
from apis.main import app

# from skywalking import agent, config
#
# config.init(
#     agent_collector_backend_services="10.0.0.125:11800",
#     agent_name="fooocus",
# )
# config.plugin_fastapi_collect_http_params = True
# agent.start()
#
# if platform.system().lower() == "windows":
#     worker = ["celery", "-A", "works.main.app", "worker", "--loglevel=INFO", "-P", "eventlet", "-c", "3"]
# else:
#     worker = ["celery", "-A", "works.main.app", "worker", "--loglevel=INFO", "-c", "3"]
# beat = ["celery", "-A", "works.main.app", "beat", "--loglevel=INFO"]


# 打开或创建一个文件来存储输出
# with open('logs/celery_worker_output.log', 'a', encoding='utf-8') as output_file, \
#         open('logs/celery_worker_error.log', 'a', encoding='utf-8') as error_file:
#     # 使用 Popen 启动进程，并将 stdout 和 stderr 重定向到文件
#     worker_process = subprocess.Popen(
#         worker,
#         stdout=output_file,
#         stderr=error_file
#     )
#     beat_process = subprocess.Popen(beat, stdout=output_file, stderr=error_file)

uvicorn.run(app, host="0.0.0.0", port=8000)
