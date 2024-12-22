"""Common model for requests"""
from enum import Enum
from typing import List
from pydantic import (
    BaseModel,
    Field,
    StrictStr
)
from apis.models.base import (
    DescribeImageType, EnhanceCtrlNets, ImagePrompt,
    Lora,
    UpscaleOrVaryMethod,
    OutpaintExpansion
)
from apis.models.remote_host import RemoteHost


loras = []
for i in range(5):
    loras.append(Lora(
        enabled=True,
        model_name='None',
        weight=0.01
    ))

class Performance(Enum):
    QUALITY = 'Quality'
    SPEED = 'Speed'
    EXTREME_SPEED = 'Extreme Speed'
    LIGHTNING = 'Lightning'
    HYPER_SD = 'Hyper-SD'

class CommonRequest(BaseModel):
    """Common request model for all requests"""
    prompt: str = Field(default="", description="Prompt to generate image")
    negative_prompt: str = Field(default="", description="Negative prompt to filter out unwanted content")
    style_selections: List[str] = Field(default=["Fooocus V2", "Fooocus Enhance", "Fooocus Sharp"], description="Style to generate image")
    performance_selection: Performance = Field(default=Performance.SPEED, description="Performance selection")
    aspect_ratios_selection: StrictStr = Field(default="1152*896", description="Aspect ratio selection")
    image_number: int = Field(default=1, description="Image number", ge=1, le=32)
    output_format: StrictStr = Field(default="png", description="Output format")
    image_seed: int = Field(default=-1, description="Seed to generate image, -1 for random")
    read_wildcards_in_order: bool = Field(default=False, description="Read wildcards in order")
    sharpness: float = Field(default=2.0, ge=0.0, le=30.0)
    guidance_scale: float = Field(default=7.0, ge=1.0, le=30.0)
    base_model_name: StrictStr = Field(default="juggernautXL_v8Rundiffusion.safetensors", description="Base Model Name")
    refiner_model_name: StrictStr = Field("None", description="Refiner Model Name")
    refiner_switch: float = Field(default=0.8, description="Refiner Switch At", ge=0.1, le=1.0)
    loras: List[Lora] = Field(default=loras, description="Lora")

    disable_intermediate_results: bool = Field(default=False, description="Disable intermediate results")
    disable_seed_increment: bool = Field(default=False, description="Disable seed increment")
    black_out_nsfw: bool = Field(default=False, description="Black out NSFW")
    adm_scaler_positive: float = Field(default=1.5, ge=0.0, le=3.0, description="The scaler multiplied to positive ADM (use 1.0 to disable).")
    adm_scaler_negative: float = Field(default=0.8, ge=0.0, le=3.0, description="The scaler multiplied to negative ADM (use 1.0 to disable).")
    adm_scaler_end: float = Field(default=0.3, ge=0.0, le=1.0, description="ADM Guidance End At Step")
    adaptive_cfg: float = Field(default=7.0, ge=1.0, le=30.0, description="Adaptive cfg")
    clip_skip: int = Field(default=2, ge=1, le=12, description="Clip skip")
    sampler_name: StrictStr = Field(default="dpmpp_2m_sde_gpu", description="Sampler name")
    scheduler_name: StrictStr = Field(default="karras", description="Scheduler name")
    vae_name: StrictStr = Field(default="Default (model)", description="VAE name")
    overwrite_step: int = Field(default=-1, description="Overwrite step")
    overwrite_switch: int = Field(default=-1, description="Overwrite switch")
    overwrite_vary_strength: float = Field(default=-1, ge=-1, le=1.0, description="Overwrite vary strength")
    overwrite_upscale_strength: float = Field(default=-1, ge=-1, le=1.0, description="Overwrite upscale strength")
    mixing_image_prompt_and_vary_upscale: bool = Field(default=False, description="Mixing image prompt and vary upscale")
    mixing_image_prompt_and_inpaint: bool = Field(default=False, description="Mixing image prompt and inpaint")
    debugging_cn_preprocessor: bool = Field(default=False, description="Debugging cn preprocessor")
    skipping_cn_preprocessor: bool = Field(default=False, description="Skipping cn preprocessor")
    canny_low_threshold: int = Field(default=64, ge=1, le=255, description="Canny Low Threshold")
    canny_high_threshold: int = Field(default=128, ge=1, le=255, description="Canny High Threshold")
    refiner_swap_method: StrictStr = Field(default="joint", description="Refiner Swap Method")
    controlnet_softness: float = Field(default=0.25, ge=0.0, le=1.0, description="ControlNet Softness")
    freeu_enabled: bool = Field(default=False, description="Enable freeu")
    freeu_b1: float = Field(default=1.01, description="Freeu B1")
    freeu_b2: float = Field(default=1.02, description="Freeu B2")
    freeu_s1: float = Field(default=0.99, description="Freeu S1")
    freeu_s2: float = Field(default=0.95, description="Freeu S2")

    preset: str = Field(default='initial', description="Presets")

    filter_hosts: RemoteHost = Field(
        default=RemoteHost(
            host_name='',
            host_ip='',
            video_ram=8192,
            labels={}
        ), description="Filter Hosts")



class UpscaleVary(CommonRequest):
    uov_method: UpscaleOrVaryMethod = Field(default=UpscaleOrVaryMethod.disable, description="Upscale or Vary Method")
    uov_input_image: StrictStr | None = Field(default="None", description="Upscale or Vary Input Image")
    upscale_multiple: float = Field(default=1.0, ge=1.0, le=5.0, description="Upscale Rate, use only when uov_method is 'Upscale (Custom)'")


class InpaintOutpaint(CommonRequest):
    inpaint_input_image: StrictStr | None = Field(default="None", description="Inpaint Input Image")
    inpaint_additional_prompt: StrictStr = Field(default="", description="Additional prompt for inpaint")
    inpaint_mask_image_upload: str | None = Field(default="None", description="Inpaint Mask Image Upload")

    outpaint_selections: List[OutpaintExpansion] = Field(default=[], description="Outpaint Expansion")
    outpaint_distance: List[int] = Field(default=[0, 0, 0, 0], description="Outpaint Distance, number in list means [left, top, right, bottom]")

    inpaint_disable_initial_latent: bool = Field(default=False, description="Disable initial latent")
    inpaint_engine: StrictStr = Field(default="v2.6", description="Inpaint Engine")
    inpaint_strength: float = Field(default=1.0, ge=0.0, le=1.0, description="Inpaint Denoising Strength")
    inpaint_respective_field: float = Field(default=0.618, ge=0.0, le=1.0,
                                            description="""
                                            Inpaint Respective Field
                                            The area to inpaint.
                                            Value 0 is same as "Only Masked" in A1111.
                                            Value 1 is same as "Whole Image" in A1111.
                                            Only used in inpaint, not used in outpaint.
                                            (Outpaint always use 1.0)
                                            """)
    inpaint_advanced_masking_checkbox: bool = Field(default=False, description="Inpaint Advanced Masking Checkbox")
    invert_mask_checkbox: bool = Field(default=False, description="Inpaint Invert Mask Checkbox")
    inpaint_erode_or_dilate: int = Field(default=0, ge=-64, le=64, description="Inpaint Erode or Dilate")


class ImagePrompt(CommonRequest):
    controlnet_image: List[ImagePrompt] = Field(default=[ImagePrompt()], description="ControlNet Image Prompt")


class ImageEnhance(CommonRequest):
    enhance_input_image: str | None = Field(default="None", description="Enhance Input Image")
    enhance_checkbox: bool = Field(default=False, description="Enhance Checkbox")
    enhance_uov_method: UpscaleOrVaryMethod = Field(default=UpscaleOrVaryMethod.disable, description="Upscale or Vary Method")
    enhance_uov_processing_order: str = Field(default='Before First Enhancement', description="Enhance UOV Processing Order, one of [Before First Enhancement, After Last Enhancement]")
    enhance_uov_prompt_type: str = Field(default='Original Prompts', description="One of 'Last Filled Enhancement Prompts', 'Original Prompts', work with enhance_uov_processing_order='After Last Enhancement'")
    enhance_ctrls: List[EnhanceCtrlNets] = Field(default=[], description="Enhance Control Nets")
    debugging_dino: bool = Field(default=False, description="Debugging DINO")
    dino_erode_or_dilate: int = Field(default=0, ge=-64, le=64, description="DINO Erode or Dilate")



class DescribeImageRequest(BaseModel):
    image: str = Field(description="Image url or base64")
    image_type: DescribeImageType = Field(default=DescribeImageType.photo, description="Image type, 'Photo' or 'Anime'")
