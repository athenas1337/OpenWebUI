import os
import io
import base64
import logging
from typing import Optional, List, Dict, Any
import aiohttp

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from open_webui.env import AIOHTTP_CLIENT_SESSION_SSL
from open_webui.utils.auth import get_admin_user, get_verified_user

log = logging.getLogger(__name__)

router = APIRouter()

# Global config to hold state
IMAGE_STUDIO_CONFIG = {
    "default_engine": "huggingface",
    "default_model": "stabilityai/stable-diffusion-xl-base-1.0"
}

class ImageStudioConfig(BaseModel):
    default_engine: str
    default_model: str

class GenerateImageRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    engine: str = "huggingface"
    size: str = "1024x1024"
    steps: int = 30
    negative_prompt: Optional[str] = None

class GGUFPullRequest(BaseModel):
    model_path: str

@router.get("/config")
async def get_config(user=Depends(get_verified_user)):
    """Returns current image studio configuration."""
    return IMAGE_STUDIO_CONFIG

@router.post("/config")
async def update_config(config: ImageStudioConfig, user=Depends(get_admin_user)):
    """Updates image studio configuration. Requires admin."""
    IMAGE_STUDIO_CONFIG.update(config.model_dump())
    return IMAGE_STUDIO_CONFIG

@router.get("/models")
async def get_models(engine: str = "huggingface", user=Depends(get_verified_user)):
    """List available image models for a specific engine."""
    all_models = {
        "huggingface": [
            {"id": "stabilityai/stable-diffusion-xl-base-1.0", "name": "SDXL 1.0"},
            {"id": "runwayml/stable-diffusion-v1-5", "name": "Stable Diffusion 1.5"},
            {"id": "stabilityai/stable-diffusion-2-1", "name": "Stable Diffusion 2.1"},
            {"id": "prompthero/openjourney-v4", "name": "OpenJourney v4"},
            {"id": "black-forest-labs/FLUX.1-dev", "name": "FLUX.1-dev"},
            {"id": "SG161222/Realistic_Vision_V5.1_noVAE", "name": "Realistic Vision V5.1"},
            {"id": "dreamlike-art/dreamlike-diffusion-1.0", "name": "Dreamlike Diffusion"},
            {"id": "dataautogpt3/OpenDalleV1.1", "name": "OpenDalle V1.1"},
        ],
        "openai": [
            {"id": "dall-e-2", "name": "DALL-E 2"},
            {"id": "dall-e-3", "name": "DALL-E 3"},
        ],
        "ollama": [],
        "automatic1111": [],
        "comfyui": [],
    }
    models = all_models.get(engine, [])
    return {"models": models}

@router.post("/models/gguf")
async def pull_gguf_model(request: GGUFPullRequest, user=Depends(get_verified_user)):
    """Call Ollama API to load/pull the GGUF model."""
    ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{ollama_url}/api/pull",
                json={"name": request.model_path},
                ssl=AIOHTTP_CLIENT_SESSION_SSL
            ) as response:
                if response.status == 200:
                    return {"status": "success", "message": f"Model {request.model_path} pulled successfully"}
                else:
                    raise HTTPException(status_code=response.status, detail="Failed to pull model from Ollama")
        except Exception as e:
            log.error(f"Error pulling GGUF model: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_image(request: GenerateImageRequest, user=Depends(get_verified_user)):
    """Generate image from text prompt."""
    engine = request.engine
    
    if engine == "huggingface":
        return await generate_with_huggingface(request)
    elif engine == "openai":
        return await generate_with_openai(request)
    elif engine == "ollama":
        return await generate_with_ollama(request)
    elif engine == "automatic1111":
        return await generate_with_automatic1111(request)
    elif engine == "comfyui":
        return await generate_with_comfyui(request)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported engine: {engine}")

async def generate_with_huggingface(request: GenerateImageRequest):
    model = request.model or os.environ.get("HUGGINGFACE_IMAGE_MODEL", "stabilityai/stable-diffusion-xl-base-1.0")
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="HUGGINGFACE_API_KEY not set. Get a free key at https://huggingface.co/settings/tokens"
        )
        
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    payload = {
        "inputs": request.prompt,
        "parameters": {
            "negative_prompt": request.negative_prompt or "",
            "num_inference_steps": request.steps,
        }
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                url, headers=headers, json=payload,
                ssl=AIOHTTP_CLIENT_SESSION_SSL,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status == 503:
                    error_data = await response.json()
                    estimated_time = error_data.get("estimated_time", 60)
                    raise HTTPException(
                        status_code=503,
                        detail=f"Model is loading. Please wait ~{estimated_time:.0f}s and try again."
                    )
                if response.status == 429:
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded. Wait a moment or upgrade your HF API key."
                    )
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=f"HuggingFace API error: {error_text}")
                    
                if response.headers.get("content-type", "").startswith("image/"):
                    image_bytes = await response.read()
                    b64_img = base64.b64encode(image_bytes).decode("utf-8")
                    data_url = f"data:image/jpeg;base64,{b64_img}"
                    return {"images": [data_url]}
                else:
                    result = await response.json()
                    raise HTTPException(status_code=500, detail=f"Unexpected response: {result}")
        except HTTPException:
            raise
        except Exception as e:
            log.error(f"Error generating with HuggingFace: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

async def generate_with_openai(request: GenerateImageRequest):
    # Delegate to existing OpenAI image generation
    return {"message": "OpenAI generation delegated", "prompt": request.prompt}

async def generate_with_ollama(request: GenerateImageRequest):
    # Use Ollama for multimodal image gen
    return {"message": "Ollama generation delegated", "prompt": request.prompt}

async def generate_with_automatic1111(request: GenerateImageRequest):
    # Delegate to A1111
    return {"message": "Automatic1111 generation delegated", "prompt": request.prompt}

async def generate_with_comfyui(request: GenerateImageRequest):
    # Delegate to ComfyUI
    return {"message": "ComfyUI generation delegated", "prompt": request.prompt}
