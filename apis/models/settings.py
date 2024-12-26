from enum import Enum

from pydantic import BaseModel, Field

from tools.llm_client import prompts


class LlmList(Enum):
    openai = "openai"
    doubao = "doubao"
    qianwen = "qianwen"
    zhipu = "zhipu"
    kimi = "kimi"
    deepseek = "deepseek"
    hunyuan = "hunyuan"
    custom = "custom"

class BaseUrlList(Enum):
    openai: str = "https://api.openai.com/v1"
    qianwen: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    doubao: str = "https://ark.cn-beijing.volces.com/api/v3"
    deepseek: str = "https://api.deepseek.com"
    kimi: str = "https://api.moonshot.cn/v1"
    hunyuan: str = "https://api.hunyuan.cloud.tencent.com/v1"

class LlmSetting(BaseModel):
    enabled: bool = Field(default=False, description="Enable LLM")
    choice: LlmList = Field(default=LlmList.openai, description="LLM model")
    api_key: str = Field(default="", description="LLM API key")
    text_model: str = Field(default="gpt-4o", description="Model choice for text to text")
    image_model: str = Field(default="None", description="Model choice for image to text")
    max_tokens: int = Field(default=4096, description="Max tokens")
    temperature: float = Field(default=0.7, description="Temperature")
    prompt_optimize: str = Field(default="None", description="system prompt for optimize")
    prompt_translate: str = Field(default="None", description="system prompt for translate")
    base_url: str = Field(default="None", description="Base URL for the LLM API")

    def __init__(self, **data):
        super().__init__(**data)
        if self.choice != LlmList.zhipu and self.base_url == "None":
            self.base_url = BaseUrlList.__getitem__(self.choice.value).value

        if self.prompt_optimize == "None" and self.choice == LlmList.openai:
            self.prompt_optimize = prompts.prompt_optimize_en_gpt
        else:
            self.prompt_optimize = prompts.prompt_optimize_zh_gpt

        if self.prompt_translate == "None" and self.choice == LlmList.openai:
            self.prompt_translate = prompts.prompt_translate_en
        else:
            self.prompt_translate = prompts.prompt_translate_zh


class TransList(Enum):
    qcloud = "qcloud"
    aliyun = "aliyun"
    baidu = "baidu"
    # google = "google"
    llm = "llm"

class TransSetting(BaseModel):
    """
    This can use for baidu, aliyun, qcloud, if choice is baidu, give app_id to access_key_id
        and app_key to access_key_secret
    """
    enabled: bool = Field(default=False, description="Enable translation")
    choice: TransList = Field(default=TransList.qcloud, description="Translation model")
    access_key_id: str = Field(default="", description="Translation API key")
    access_key_secret: str = Field(default="", description="Translation API secret")
    endpoint: str = Field(default="", description="Translation API endpoint")
    region: str = Field(default="", description="Translation region, Ali translate no need this")


class OssList(Enum):
    aliyun = "aliyun"
    qcloud = "qcloud"
    qiniu = "qiniu"
    # s3 = "s3"
    # google = "google"

class OssSetting(BaseModel):
    enabled: bool = Field(default=False, description="Enable OSS")
    choice: OssList = Field(default=OssList.aliyun, description="服务提供商，如 aliyun, qcloud, qiniu, s3, google")
    access_key_id: str = Field(default="", description="OSS access key id")
    access_key_secret: str = Field(default="", description="OSS access key secret")
    bucket: str = Field(default="", description="OSS bucket name")
    endpoint: str = Field(default="", description="OSS endpoint, QCloud no need this")
    region: str = Field(default="", description="OSS region")

class Settings(BaseModel):
    """
    This can use for all service
    """
    id: str = Field(default="default", description="Setting id")
    llm: LlmSetting = Field(default=LlmSetting(), description="LLM setting")
    translation: TransSetting = Field(default=TransSetting(), description="Translation setting")
    oss: OssSetting = Field(default=OssSetting(), description="OSS setting")
