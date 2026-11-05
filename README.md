# Vidora

AI-powered YouTube video creation platform. The current backend prototype provides AI script generation through OpenAI, Google Gemini, or Anthropic Claude.

## Run the API

1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set the provider and its API key in your local environment. Never commit real API keys. You can copy `.env.example` as a reference; the application reads environment variables and does not automatically load a `.env` file.

   **Windows PowerShell example for Gemini**
   ```powershell
   $env:AI_PROVIDER="gemini"
   $env:GEMINI_API_KEY="your-gemini-api-key"
   ```

   **macOS/Linux example for Gemini**
   ```bash
   export AI_PROVIDER="gemini"
   export GEMINI_API_KEY="your-gemini-api-key"
   ```

   For OpenAI, set `AI_PROVIDER=openai` and `OPENAI_API_KEY`. For Claude, set `AI_PROVIDER=anthropic` and `ANTHROPIC_API_KEY`. Model names can be customized using `OPENAI_MODEL`, `GEMINI_MODEL`, or `ANTHROPIC_MODEL`.

5. Start the server:

   ```bash
   uvicorn main:app --reload
   ```

6. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to try the interactive API.

## Script generation endpoint

`POST /generate-script`

Example request:

```json
{
  "topic": "What if Earth suddenly stopped spinning?",
  "duration_seconds": 30,
  "style": "cinematic and engaging YouTube Short narration",
  "language": "English",
  "provider": "gemini"
}
```

The `provider` field is optional. If omitted, Vidora uses `AI_PROVIDER`, which defaults to `openai`. Supported values are `openai`, `gemini`, and `anthropic`. Each provider requires its own API key and account access.

## Current status

This is an early backend prototype. Text-to-speech, visual generation, video editing, user accounts, and export workflows have not yet been implemented. Provider API calls have not been verified against live credentials in this repository change.
