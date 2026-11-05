import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Vidora API", version="0.2.0")


class ScriptRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    duration_seconds: int = Field(default=60, ge=15, le=600)
    style: str = Field(default="engaging YouTube narration", max_length=120)
    language: str = Field(default="English", max_length=80)


@app.get("/")
def home():
    return {
        "app": "Vidora",
        "message": "Vidora script generation API is running.",
        "docs": "/docs",
    }


@app.post("/generate-script")
async def generate_script(request: ScriptRequest):
    """Generate a video script with the OpenAI API."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="AI script generation is not configured. Set OPENAI_API_KEY in your environment.",
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    prompt = (
        "Write a complete YouTube narration script. Make it original, clear, "
        "well-paced, and suitable for spoken delivery. Include a compelling "
        "opening hook, a coherent body, and a satisfying ending. Do not include "
        "production notes or claim unsupported facts. Return only the script.\n\n"
        f"Topic: {request.topic}\n"
        f"Target duration: about {request.duration_seconds} seconds\n"
        f"Style: {request.style}\n"
        f"Language: {request.language}"
    )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are Vidora, a professional YouTube script writer.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                },
            )
            response.raise_for_status()
            data = response.json()
        script = data["choices"][0]["message"]["content"]
        if not script:
            raise ValueError("The model returned an empty script.")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail="The AI provider returned an error. Check the API key, model, and account billing.",
        ) from exc
    except (httpx.RequestError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Vidora could not get a valid script from the AI provider.",
        ) from exc

    return {
        "topic": request.topic,
        "duration_seconds": request.duration_seconds,
        "style": request.style,
        "language": request.language,
        "script": script,
        "generated_by": model,
    }
