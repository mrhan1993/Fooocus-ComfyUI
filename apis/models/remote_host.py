from typing import Dict, List, Optional
from pydantic import (
    BaseModel,
    Field
)


class BaseAttributes(BaseModel):
    """
    Base attributes model
    Attributes:
        video_ram (int): Video memory, MB
        memory (int): Memory, MB
        cpu_cores (int): CPU cores
        gpu_model (str): GPU model
        flops (float): Flops, M
        labels (dict): Tags
    """
    video_ram: Optional[int] = Field(default=0, ge=0, description="Video memory, MB")
    memory: Optional[int] = Field(default=0, ge=0, description="Memory, MB")
    cpu_cores: Optional[int] = Field(default=0, ge=0, description="CPU cores")
    gpu_model: Optional[str] = Field(default="", description="GPU model")
    flops: Optional[float] = Field(default=0.0, ge=0, description="Flops, M")
    labels: Dict[str, str] = Field(default={}, description="Tags")


class FilterHost(BaseAttributes):
    """
    Filter host model
    Attributes:
        host_name (str): Host name, Optional
        host_ip (str): Host ip, Optional
    """
    host_name: Optional[str] = Field(default="", description="Host name")
    host_ip: Optional[str] = Field(default="", description="Host ip")


class RemoteHost(BaseAttributes):
    """
    Remote host model
    Attributes:
        enabled (bool): Enabled, Optional, default=True
        host_name (str): Host name, Required
        host_ip (str): Host ip, Required
        host_port (int): Host port, Optional, default=8188
    """
    enabled: bool = Field(default=True, description="Enabled")
    host_name: str = Field(description="Host name")
    host_ip: str = Field(description="Host ip")
    host_port: int = Field(default=8188, description="Host port")

    class Config:
        extra = "allow"


class RemoteHostDB(RemoteHost):
    """
    Remote host model
    Attributes:
        alive (bool): is host alive, Optional, default=True
    """
    alive: bool = Field(default=True, description="Is host alive")


class RemoteHosts(BaseModel):
    """
    Remote host model
    Attributes:
        hosts (list[RemoteHost]): Hosts, Optional
    """
    hosts: List[RemoteHost] = Field(default=[], description="Hosts")


class RemoteHostsDB(BaseModel):
    """
    Remote host model
    Attributes:
        hosts (list[RemoteHostDB]): Hosts, Optional
    """
    hosts: List[RemoteHostDB] = Field(default=[], description="Hosts")
