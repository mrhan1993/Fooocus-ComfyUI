FROM python:3.12-bullseye

WORKDIR /app

COPY . /app

RUN apt update && \
    apt install -y --no-install-recommends \
    g++ && apt clean

RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "run.py"]