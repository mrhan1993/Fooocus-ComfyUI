from typing import Dict, List

from pydantic import (
    BaseModel,
    Field
)


class RemoteHost(BaseModel):
    host_name: str = Field(description="Host name")
    host_ip: str = Field(description="Host ip")
    host_port: int = Field(default=8188, description="Host port")
    video_ram: int = Field(default=0, description="Video memory, MB")
    memory: int = Field(default=0, description="Memory, MB")
    cpu_cores: int = Field(default=0, description="CPU cores")
    gpu_model: str = Field(default="", description="GPU model")
    flops: float = Field(default=0.0, description="Flops, M")
    labels: dict = Field(default={}, description="Tags")

class RemoteHosts(BaseModel):
    hosts: List[RemoteHost] = Field(default=[], description="Hosts")
