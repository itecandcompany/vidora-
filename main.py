from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Vidora API", version="0.1.0")


class ScriptRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    duration_seconds: int = Field(default=60, ge=15, le=600)


@app.get("/")
def home():
    return {"app": "Vidora", "message": "AI-powered video creation API is running."}


@app.post("/generate-script")
def generate_script(request: ScriptRequest):
    """Temporary placeholder; replace with an AI model integration next."""
    script = (
        f"Welcome to Vidora! Today, we're exploring {request.topic}. "
        f"This video is planned for approximately {request.duration_seconds} seconds."
    )
    return {
        "topic": request.topic,
        "duration_seconds": request.duration_seconds,
        "script": script,
        "generated_by": "placeholder",
    }
