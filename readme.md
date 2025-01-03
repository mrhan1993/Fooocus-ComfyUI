该项目仍处于开发阶段

# 简介

该项目使用 Celery 和 Fooocus 实现了一个基于 ComfyUI 的异步任务系统, 主要有以下特性:

- ComfyUI 的集群化, 使用 Redis 存储 ComfyUI 实例信息
- 任务分配功能, 可以根据标签选择主机或者主机组
- 分布式任务, 根据图像生成数量拆分任务, 分配到不同的主机执行
- 基于 LLM 的提示词优化、翻译(未开启)
- 使用 OSS 存储 Input OutPut 图像(目前支持阿里和腾讯的对象存储)
- 集中化的配置管理
- 使用数据库持久化任务信息
- 基于 FastAPI 的 RestAPI

# 快速开始

该项目需要使用的服务较多, 列表如下:

- LLM: OpenAI 兼容, 暂未开启
- MachineTranslate: 机器翻译, 目前支持阿里, 腾讯以及百度, 暂未开启

以上两个相关功能未开启, 可以不进行配置

- Oss: 目前支持阿里和腾讯的对象存储, 后续扩展支持
- MySQL: 作为 Celery 后端存储, 理论上可以更换
- Redis: 作为 Celery 消息队列以及配置信息存储
- ComfyUI: 用于实际执行任务

## 服务准备

Oss:
 - 阿里: [创建AccessKey](https://help.aliyun.com/zh/ram/user-guide/create-an-accesskey-pair)
 - 腾讯: [使用永久密钥访问 COS](https://cloud.tencent.com/document/product/436/68282)

数据库:
- MySQL:
  - Host: [Installing MySQL](https://dev.mysql.com/doc/refman/8.4/en/installing.html)
  - Docker: [mysql/mysql-server](https://hub.docker.com/r/mysql/mysql-server)
- Redis: 
  - Host: [Install Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)
  - Docker: [redis](https://hub.docker.com/_/redis)

> MySQL 使用 8.x

ComfyUI:

目前只支持 Fooocus, ComfyUI 的安装可以参考官方安装文档: [Installing](https://github.com/comfyanonymous/ComfyUI?tab=readme-ov-file#installing), 
此外, 还需要安装 [EasyUse](https://github.com/yolain/ComfyUI-Easy-Use) 和 [ComfyUI-Fooocus](https://github.com/mrhan1993/ComfyUI-Fooocus) 这两个节点

## 配置 Celery

在 `configs/celery_config.py` 中有一个配置示例, 根据上面准备好的服务, 改动 `broker_url` 和 `result_backend` 即可.

> 你需要在 MySQL 中预先创建数据库, Celery 会自动创建表结构, 如果有需要, 可能还要改动 `timezone`,
> 该文件为纯粹的 Celery 配置, 完整的配置可以参考 [Celery 配置](https://docs.celeryq.dev/en/stable/userguide/configuration.html), 
> 请注意 Celery 的 `broker_url` 同时也是程序 Redis 的配置

## 安装依赖

```shell
# 使用 venv
python -m venv venv
source venv/bin/activate

# 使用 conda
conda create -n celery python=3.12
conda activate celery

# 安装依赖
pip install requirements.txt
```

如果使用 Windows 需要额外安装 `eventlet`

## 启动

程序由 Celery 和 FastAPI 编写, 其中 Celery 分为 `beat` 和 `worker` 两个部分, `beat` 用来定时检测 ComfyUI 是否存活, `worker` 用来执行任务

> Celery beat 可以不启动, 但在节点选择时可能选择到不可用节点

启动 `beat`:

`celery -A works.main.app beat --loglevel=INFO`

启动 `worker`:

`celery -A works.main.app worker -l INFO -c ${CONCURRENCY}`

其中 `${CONCURRENCY}` 用来指定 Celery 的并发数量, 在 Windows 中需要指定时间循环使用的库, (使用 `pip install eventlet` 安装对应库):

`celery -A works.main.app worker --loglevel=INFO -P eventlet -c ${CONCURRENCY}`

启动 `FastAPI`:

`python run.py --port=8000 --host=0.0.0.0`

> 默认端口 8000, 默认绑定所有 IP

# 配置

在浏览器访问 `http://host:port/docs`, 以查看接口文档

## 添加主机

**Uri**: `/apis/v1/add_update_worker`

**Method**: Post

**Params**:
```json
{
  "hosts": [
    {
      "enabled": true,
      "host_name": "localhost",
      "host_ip": "127.0.0.1",
      "host_port": 8188,
      "video_ram": 8192,
      "memory": 16384,
      "cpu_cores": 4,
      "gpu_model": "4090",
      "flops": 82.58,
      "labels": {
        "env": "dev"
      }
    },{
      "enabled": true,
      "host_name": "worker-1",
      "host_ip": "192.168.1.2",
      "host_port": 8188,
      "video_ram": 8192,
      "memory": 16384,
      "cpu_cores": 4,
      "gpu_model": "4090",
      "flops": 82.58,
      "labels": {
        "env": "dev"
      }
    }
  ]
}
```

除说明的必选参数, 其他都可以不指定, 以下是 `host` 完整属性

- `enabled`: 是否启用该主机, 默认开启
- `host_name`: 主机名, 自定义标识, 必选参数
- `host_ip`: 主机地址, 必选参数
- `host_port`: ComfyUI 端口, 默认 `8188`, Int 类型
- `video_ram`: 显存, 单位可以自定义, 用来挑选主机时注意单位即可, Int 类型
- `memory`: 内存大小, 定义方式同 `video_ram`, Int 类型
- `cpu_cores`: CPU 核心数, Int 类型
- `gpu_model`: 显卡型号
- `flops`: 显卡算力, float 类型
- `labels`: 自定义标签, k/v 值

## 增加配置

**Uri**: `/apis/v1/save_setting`

**Method**: Post

**Params**:
```json
{
  "id": "default",
  "llm": {
    "enabled": false,
    "choice": "openai",
    "api_key": "",
    "text_model": "gpt-4o",
    "image_model": "None",
    "max_tokens": 4096,
    "temperature": 0.7,
    "prompt_optimize": "...",
    "prompt_translate": "...",
    "base_url": "https://api.openai.com/v1"
  },
  "translation": {
    "enabled": false,
    "choice": "qcloud",
    "access_key_id": "",
    "access_key_secret": "",
    "endpoint": "",
    "region": ""
  },
  "oss": {
    "enabled": false,
    "choice": "aliyun",
    "access_key_id": "",
    "access_key_secret": "",
    "bucket": "",
    "endpoint": "",
    "region": ""
  }
}
```

参数说明:
- `id`: 用来标识配置, 默认 `default`, 目前没用, 为多用户准备的
- `llm`: LlmSetting, 目前没用
- `translation`: TransSetting, 目前没用
- `oss`: OssSetting

**LlmSetting**:
- `enabled`: 是否启用, 目前没用
- `choice`: 选择使用的大语言模型, 可以选择 `openai`, `doubao`, `qianwen`, `zhipu`, `kimi`, `deepseek`, `hunyuan` 或者 `OpenAI` 兼容的模型
- `api_key`: api_key
- `text_model`: 指定使用的文本模型
- `image_model`: `gpt-4o` 是多模态模型, 可以用作反推, 智谱的 `glm-4v-flash` 也有此能力, 不支持其他模型(反推功能目前未接入)
- `max_token`: 默认 4096
- `temperature`: 默认 0.7
- `prompt_optimize`: 用于优化提示词的 `system_prompt`
- `prompt_translate`: 用于翻译的 `system_prompt`
- `base_url`: 使用 OpenAI 兼容接口时的 `base_url`, 上述提到的预定义了 `base_url`, 无需额外指定

**TransSetting**:
- `enabled`: 是否开启, 目前没用
- `choice`: `qcloud`, `aliyun`, `baidu`, `llm`, 选择 `llm` 时, 需要配置 `LlmSetting`
- `access_key_id`: access_key_id, 百度的 `app_id` 对应该选项
- `access_key_secret`: access_key_secret, 百度的 `app_key` 对应该选项
- `endpoint`: endpoint
- `region`: region, aliyun不需要该选项

> 百度只需要 `access_key_id` 和 `access_key_secret`

**OssSetting**:
- `enabled`: 没用, 必须开启
- `choice`: 目前可用 `aliyun`, `qcloud`
- `access_key_id`: access_key_id
- `access_key_secret`: access_key_secret
- `bucket`: bucket
- `endpoint`: OSS endpoint, qcloud 不需要该参数
- `region`: OSS region