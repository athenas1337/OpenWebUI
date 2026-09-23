"""
Hugging Face Inference API integration for free image generation.

This module provides a client for the Hugging Face Inference API,
which offers free access to various image generation models including
Stable Diffusion XL, FLUX, and more.

Usage:
    from open_webui.utils.images.huggingface import (
        huggingface_generate_image,
        get_huggingface_models,
    )
"""

from __future__ import annotations

import base64
import logging
import os
from typing import Optional

import aiohttp

log = logging.getLogger(__name__)

# Hugging Face Inference API endpoint
HF_INFERENCE_API_URL = "https://api-inference.huggingface.co/models"

# Popular free image generation models on Hugging Face
FREE_IMAGE_MODELS = [
    {
        "id": "stabilityai/stable-diffusion-xl-base-1.0",
        "name": "Stable Diffusion XL Base 1.0",
        "description": "High-quality 1024x1024 image generation by Stability AI",
        "free": True,
    },
    {
        "id": "runwayml/stable-diffusion-v1-5",
        "name": "Stable Diffusion v1.5",
        "description": "Classic Stable Diffusion model, fast and reliable",
        "free": True,
    },
    {
        "id": "stabilityai/stable-diffusion-2-1",
        "name": "Stable Diffusion 2.1",
        "description": "Improved SD model with better prompt following",
        "free": True,
    },
    {
        "id": "CompVis/stable-diffusion-v1-4",
        "name": "Stable Diffusion v1.4",
        "description": "Original Stable Diffusion model",
        "free": True,
    },
    {
        "id": "prompthero/openjourney-v4",
        "name": "OpenJourney v4",
        "description": "Midjourney-style image generation, free",
        "free": True,
    },
    {
        "id": "SG161222/Realistic_Vision_V5.1_noVAE",
        "name": "Realistic Vision V5.1",
        "description": "Photorealistic image generation",
        "free": True,
    },
    {
        "id": "dreamlike-art/dreamlike-diffusion-1.0",
        "name": "Dreamlike Diffusion 1.0",
        "description": "Artistic and dreamlike image generation",
        "free": True,
    },
    {
        "id": "dataautogpt3/OpenDalleV1.1",
        "name": "OpenDalle V1.1",
        "description": "Open-source DALL-E alternative",
        "free": True,
    },
]


async def huggingface_generate_image(
    prompt: str,
    model: str = "stabilityai/stable-diffusion-xl-base-1.0",
    api_key: Optional[str] = None,
    negative_prompt: Optional[str] = None,
    width: int = 1024,
    height: int = 1024,
    num_inference_steps: int = 30,
    guidance_scale: float = 7.5,
) -> dict:
    """
    Generate an image using the Hugging Face Inference API.

    Args:
        prompt: Text description of the image to generate
        model: HuggingFace model ID
        api_key: HF API key (optional but recommended for higher rate limits)
        negative_prompt: Things to avoid in the generated image
        width: Image width in pixels
        height: Image height in pixels
        num_inference_steps: Number of denoising steps
        guidance_scale: How closely to follow the prompt

    Returns:
        dict with 'image' (base64 string) and 'content_type' keys

    Raises:
        Exception: If API call fails
    """
    if not api_key:
        api_key = os.environ.get("HUGGINGFACE_API_KEY", "")

    url = f"{HF_INFERENCE_API_URL}/{model}"

    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "inputs": prompt,
        "parameters": {
            "width": width,
            "height": height,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
        },
    }

    if negative_prompt:
        payload["parameters"]["negative_prompt"] = negative_prompt

    log.info(
        "Generating image via Hugging Face: model=%s, prompt=%s",
        model,
        prompt[:100],
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120),
            ) as response:
                if response.status == 503:
                    # Model is loading, get estimated time
                    error_data = await response.json()
                    estimated_time = error_data.get("estimated_time", 60)
                    raise Exception(
                        f"Model is loading. Estimated wait: {estimated_time:.0f}s. "
                        f"Please try again in a moment."
                    )

                if response.status == 429:
                    raise Exception(
                        "Rate limit exceeded. Please wait a moment and try again, "
                        "or add a Hugging Face API key for higher limits."
                    )

                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(
                        f"Hugging Face API error ({response.status}): {error_text}"
                    )

                content_type = response.headers.get("Content-Type", "image/png")
                image_bytes = await response.read()
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")

                log.info("Image generated successfully via Hugging Face")

                return {
                    "image": image_base64,
                    "content_type": content_type,
                    "data_url": f"data:{content_type};base64,{image_base64}",
                }

    except aiohttp.ClientError as e:
        log.error("Hugging Face API connection error: %s", str(e))
        raise Exception(f"Failed to connect to Hugging Face API: {str(e)}")


def get_huggingface_models() -> list[dict]:
    """
    Get list of available free image generation models on Hugging Face.

    Returns:
        List of model dictionaries with id, name, description, and free status
    """
    return FREE_IMAGE_MODELS


async def check_model_status(
    model: str, api_key: Optional[str] = None
) -> dict:
    """
    Check if a Hugging Face model is loaded and ready.

    Args:
        model: HuggingFace model ID
        api_key: Optional API key

    Returns:
        dict with 'loaded' (bool) and 'estimated_time' (float) keys
    """
    if not api_key:
        api_key = os.environ.get("HUGGINGFACE_API_KEY", "")

    url = f"{HF_INFERENCE_API_URL}/{model}"

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return {"loaded": True, "estimated_time": 0}
                elif response.status == 503:
                    data = await response.json()
                    return {
                        "loaded": False,
                        "estimated_time": data.get("estimated_time", 60),
                    }
                else:
                    return {"loaded": False, "estimated_time": -1}
    except Exception as e:
        log.error("Error checking model status: %s", str(e))
        return {"loaded": False, "estimated_time": -1}
