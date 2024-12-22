"""Route for Fooocus
Include routes based on fooocus
    - text to image
    - upscale vary
    - inpaint outpaint
    - image prompt
    - image enhance
"""
from fastapi import APIRouter

from apis.models.requests import (
    CommonRequest,
    UpscaleVary,
    InpaintOutpaint,
    ImagePrompt,
    ImageEnhance
)


fooocus_router = APIRouter()

@fooocus_router.post(
    path="/apis/v1/fooocus/text-to-image",
    summary="Fooocus API Text to image endpoint",
    tags=["Fooocus"])
async def text_to_image(request: CommonRequest):
    """Text to image"""
    return request

@fooocus_router.post(
    path="/apis/v1/fooocus/image-upscale-vary",
    summary="Fooocus API Image upscale or vary",
    tags=["Fooocus"])
async def upscale_vary(request: UpscaleVary):
    """Upscale or vary"""
    return request

@fooocus_router.post(
    path="/apis/v1/fooocus/inpaint-outpaint",
    summary="Fooocus API Inpaint outpaint",
    tags=["Fooocus"])
async def inpaint_outpaint(request: InpaintOutpaint):
    """Inpaint outpaint"""
    return request

@fooocus_router.post(
    path="/apis/v1/fooocus/image-prompt",
    summary="Fooocus API Image Prompt",
    tags=["Fooocus"])
async def image_prompt(request: ImagePrompt):
    """Image Prompt"""
    return request

@fooocus_router.post(
    path="/apis/v1/fooocus/image-enhance",
    summary="Fooocus API Image Enhance",
    tags=["Fooocus"])
async def image_enhance(request: ImageEnhance):
    """Image Enhance"""
    return request
