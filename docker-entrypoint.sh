#!/bin/bash

cd "${WORKDIR:-/app}" || exit 1
mkdir -pv "logs"

CONCURRENCY=${CONCURRENCY:-10}
RUN_BEAT=${RUN_BEAT:-true}
RUN_WORKER=${RUN_WORKER:-true}

function beat() {
    sleep 10
    if ! pgrep -f "celery -A works.main.app beat" > /dev/null; then
        echo "Starting celery beat"
        celery -A works.main.app beat --loglevel=INFO >> logs/celery_beat.log 2>&1 &
    fi
}

function worker() {
    sleep 10
    if ! pgrep -f "celery -A works.main.app worker" > /dev/null; then
        echo "Starting celery worker"
        celery -A works.main.app worker -l INFO -c "${CONCURRENCY}" \
          --loglevel=INFO | grep -v 'check_worker' >> logs/celery_worker.log 2>&1 &
    fi
}

# 捕获脚本退出信号，清理后台进程
trap 'pkill -f "celery -A works.main.app"' EXIT

# 启动 worker 和 beat
if [ "${RUN_WORKER}" = "true" ]; then
  while true; do worker; done >> /dev/null 2>&1 &
fi

if [ "${RUN_BEAT}" = "true" ]; then
  while true; do beat; done >> /dev/null 2>&1 &
fi

exec "$@"