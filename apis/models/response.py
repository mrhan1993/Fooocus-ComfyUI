"""
The response model is used to define the structure of the response object that will be returned by the API.
"""
from typing import List
from pydantic import (
    BaseModel,
    ConfigDict, Field
)


class AllModelNamesResponse(BaseModel):
    """
    all model list response
    """
    model_filenames: List[str] = Field(description="All available model filenames")
    lora_filenames: List[str] = Field(description="All available lora filenames")

    model_config = ConfigDict(
        protected_namespaces=('protect_me_', 'also_protect_')
    )
