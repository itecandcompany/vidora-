import os
from pathlib import Path
from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Vidora API", version="0.3.0")

Provider = Literal["openai", "gemini", "anthropic"]


class ScriptRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    duration_seconds: int = Field(default=60, ge=15, le=600)
    style: str = Field(default="engaging YouTube narration", max_length=120)
    language: str = Field(default="English", max_length=80)
    provider: Provider | None = Field(
        default=None,
        description="AI provider: openai, gemini, or anthropic. Defaults to AI_PROVIDER.",
    )


@app.get("/")
def home():
    """Serve the Vidora web interface."""
    return FileResponse(Path(__file__).parent / "static" / "index.html")


def build_prompt(request: ScriptRequest) -> str:
    return (
        "Write a complete YouTube narration script. Make it original, clear, "
        "well-paced, and suitable for spoken delivery. Include a compelling "
        "opening hook, a coherent body, and a satisfying ending. Do not include "
        "production notes or claim unsupported facts. Return only the script.\n\n"
        f"Topic: {request.topic}\n"
        f"Target duration: about {request.duration_seconds} seconds\n"
        f"Style: {request.style}\n"
        f"Language: {request.language}"
    )


async def generate_with_openai(client: httpx.AsyncClient, prompt: str, api_key: str, model: str) -> str:
    response = await client.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "You are Vidora, a professional YouTube script writer."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        },
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


async def generate_with_gemini(client: httpx.AsyncClient, prompt: str, api_key: str, model: str) -> str:
    response = await client.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        params={"key": api_key},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7},
        },
    )
    response.raise_for_status()
    data = response.json()
    parts = data["candidates"][0]["content"]["parts"]
    return "\n".join(part["text"] for part in parts if "text" in part)


async def generate_with_anthropic(client: httpx.AsyncClient, prompt: str, api_key: str, model: str) -> str:
    response = await client.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": model,
            "max_tokens": 2048,
            "system": "You are Vidora, a professional YouTube script writer.",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        },
    )
    response.raise_for_status()
    data = response.json()
    return "\n".join(block["text"] for block in data["content"] if block.get("type") == "text")


@app.post("/generate-script")
async def generate_script(request: ScriptRequest):
    """Generate a YouTube narration script using the selected AI provider."""
    provider = (request.provider or os.getenv("AI_PROVIDER", "openai")).lower()
    if provider not in ("openai", "gemini", "anthropic"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported AI provider. Choose openai, gemini, or anthropic.",
        )

    provider_config = {
        "openai": (os.getenv("OPENAI_API_KEY"), os.getenv("OPENAI_MODEL", "gpt-4.1-mini")),
        "gemini": (os.getenv("GEMINI_API_KEY"), os.getenv("GEMINI_MODEL", "gemini-2.5-flash")),
        "anthropic": (
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-latest"),
        ),
    }
    api_key, model = provider_config[provider]
    if not api_key:
        key_name = {
            "openai": "OPENAI_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
        }[provider]
        raise HTTPException(
            status_code=503,
            detail=f"{provider.capitalize()} script generation is not configured. Set {key_name} in your environment.",
        )

    prompt = build_prompt(request)
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            if provider == "openai":
                script = await generate_with_openai(client, prompt, api_key, model)
            elif provider == "gemini":
                script = await generate_with_gemini(client, prompt, api_key, model)
            else:
                script = await generate_with_anthropic(client, prompt, api_key, model)

        if not script or not script.strip():
            raise ValueError("The model returned an empty script.")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"The {provider} provider returned an error. Check the API key, model, and account access.",
        ) from exc
    except (httpx.RequestError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Vidora could not get a valid script from the {provider} provider.",
        ) from exc

    return {
        "topic": request.topic,
        "duration_seconds": request.duration_seconds,
        "style": request.style,
        "language": request.language,
        "provider": provider,
        "script": script,
        "generated_by": model,
    }
