from typing import Dict, List, Optional
from pydantic import (
    BaseModel,
    Field
)


class FilterHost(BaseModel):
    """
    Filter host model
    Attributes:
        host_name (str): Host name, Optional
        host_ip (str): Host ip, Optional
        video_ram (int): Video memory, MB, Optional
        memory (int): Memory, MB, Optional
        cpu_cores (int): CPU cores, Optional
        gpu_model (str): GPU model, Optional
        flops (float): Flops, M, Optional
        labels (dict): Tags, Optional
    """
    host_name: Optional[str] = Field(default="", description="Host name")
    host_ip: Optional[str] = Field(default="", description="Host ip")
    video_ram: Optional[int] = Field(default=0, ge=0, description="Video memory, MB")
    memory: Optional[int] = Field(default=0, ge=0, description="Memory, MB")
    cpu_cores: Optional[int] = Field(default=0, ge=0, description="CPU cores")
    gpu_model: Optional[str] = Field(default="", description="GPU model")
    flops: Optional[float] = Field(default=0, ge=0, description="Flops, M")
    labels: Optional[Dict[str, str]] = Field(default={}, description="Tags")


class RemoteHost(BaseModel):
    """
    Remote host model
    Attributes:
        host_name (str): Host name, Required
        host_ip (str): Host ip, Required
        host_port (int): Host port, Optional, default=8188
        video_ram (int): Video memory, MB, Optional, default=0
        memory (int): Memory, MB, Optional, default=0
        cpu_cores (int): CPU cores, Optional, default=0
        gpu_model (str): GPU model, Optional, default=""
        flops (float): Flops, M, Optional, default=0
        labels (dict): Tags, Optional, default={},
    """
    host_name: str = Field(description="Host name")
    host_ip: str = Field(description="Host ip")
    host_port: int = Field(default=8188, description="Host port")
    video_ram: int = Field(default=0, ge=0, description="Video memory, MB")
    memory: int = Field(default=0, ge=0, description="Memory, MB")
    cpu_cores: int = Field(default=0, ge=0, description="CPU cores")
    gpu_model: str = Field(default="", description="GPU model")
    flops: float = Field(default=0.0, ge=0, description="Flops, M")
    labels: Dict[str, str] = Field(default={}, description="Tags")

    class Config:
        extra = "allow"

class RemoteHosts(BaseModel):
    """
    Remote host model
    Attributes:
        hosts (list[RemoteHost]): Hosts, Optional
    """
    hosts: List[RemoteHost] = Field(default=[], description="Hosts")
