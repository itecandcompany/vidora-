# Vidora

AI-powered YouTube video creation platform. This repository currently contains the first backend feature: AI script generation.

## Run the API

1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set your OpenAI API key in your local environment. Do not commit API keys.

   **Windows PowerShell**
   ```powershell
   $env:OPENAI_API_KEY="your-api-key"
   ```

   **macOS/Linux**
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

   Optionally set `OPENAI_MODEL` to a model available to your API account. The default is `gpt-4.1-mini`.

5. Start the server:

   ```bash
   uvicorn main:app --reload
   ```

6. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to try the interactive API.

## First endpoint

`POST /generate-script`

Example request:

```json
{
  "topic": "How artificial intelligence is changing education",
  "duration_seconds": 120,
  "style": "engaging and informative",
  "language": "English"
}
```

The endpoint returns the generated narration script as JSON. It needs a valid `OPENAI_API_KEY`; without one, it returns a clear configuration error.

## Current status

This is an early backend prototype. The web dashboard, text-to-speech, visual generation, video editing, user accounts, and export workflow have not been implemented yet.
