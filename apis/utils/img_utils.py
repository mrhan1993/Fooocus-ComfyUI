"""
Image process utils. Used to verify, convert and store Images.

@file: img_utils.py
@author: Konie
@update: 2024-03-23
"""
import base64
import hashlib
import imghdr
from io import BytesIO

import numpy as np
import requests
from PIL import Image
from fastapi import UploadFile


def get_ext_from_bytes(file_bytes: bytes) -> str:
    image_type = imghdr.what(None, h=file_bytes)
    if image_type:
        return f".{image_type}"
    else:
        return "png"


def convert_image(image_path: str, image_format: str = 'png') -> bytes | None:
    """
    Convert image to another format
    Args:
        image_path (str): Image path
        image_format (str): Image format
    Returns:
        BytesIO: Image bytes
    """
    try:
        img = Image.open(image_path)
        image_bytes = BytesIO()
        img.save(image_bytes, format=image_format.upper())
        image_bytes.seek(0)
    except Exception as e:
        print(e)
        return
    return image_bytes.getvalue()


def narray_to_base64img(narray: np.ndarray) -> str | None:
    """
    Convert numpy array to base64 image string.
    Args:
        narray: numpy array
    Returns:
        base64 image string
    """
    if narray is None:
        return None

    img = Image.fromarray(narray)
    output_buffer = BytesIO()
    img.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode('utf-8')
    return base64_str


def narray_to_bytesimg(narray) -> bytes | None:
    """
    Convert numpy array to bytes image.
    Args:
        narray: numpy array
    Returns:
        bytes image
    """
    if narray is None:
        return None

    img = Image.fromarray(narray)
    output_buffer = BytesIO()
    img.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    return byte_data


def get_check_image(url: str) -> UploadFile | None:
    """
    Get image from url and check if it's valid.
    Args:
        url: image url
    Returns:
        UploadFile or None
    """
    if url == '':
        return None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        binary_image = response.content
    except Exception:
        return None
    try:
        buffer = BytesIO(binary_image)
        Image.open(buffer)  # This validates the image
    except Exception:
        return None
    byte_stream = BytesIO()
    byte_stream.write(binary_image)
    byte_stream.seek(0)
    return UploadFile(file=byte_stream)


def base64_to_bytesimg(base64_str: str) -> bytes | None:
    """
    Convert base64 image string to bytes image.
    Args:
        base64_str: base64 image string
    Returns:
        bytes image or None
    """
    if base64_str == '':
        return None
    bytes_image = base64.b64decode(base64_str)
    return bytes_image


def base64_to_narray(base64_str: str) -> np.ndarray | None:
    """
    Convert base64 image string to numpy array.
    Args:
        base64_str: base64 image string
    Returns:
        numpy array or None
    """
    if base64_str == '':
        return None
    bytes_image = base64.b64decode(base64_str)
    image = np.frombuffer(bytes_image, np.uint8)
    return image


def sha256_from_base64(base64_str: str) -> str | None:
    """
    Calculate SHA256 hash from base64 image string.
    Args:
        base64_str: base64 image string
    Returns:
        SHA256 hash or None
    """
    if base64_str == '':
        return None
    bytes_image = base64.b64decode(base64_str)
    return hashlib.sha256(bytes_image).hexdigest()


def base64_from_path(path: str) -> str | None:
    """
    Convert image path to base64 image string.
    Args:
        path: image path
    Returns:
        base64 image string or None
    """
    if path == '':
        return None
    with open(path, 'rb') as f:
        bytes_image = f.read()
    base64_str = base64.b64encode(bytes_image).decode('utf-8')
    return base64_str
