from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google import genai
import os
import requests
from bs4 import BeautifulSoup

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/text/")
async def analyze_text(
    text: str = Form(""),                 # optional text
    url: str = Form(""),                  # optional url
    file: UploadFile = File(None)         # optional image
):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables!")

    client = genai.Client(api_key=api_key)

    # make sure at least one input exists
    if not text.strip() and not url.strip() and not file:
        raise HTTPException(status_code=400, detail="Provide text, url, or image")

    try:
        # --- case: url provided ---
        if url.strip():
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/123.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, verify=False)
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
            return {"content": text}
        # --- case: text + image ---
        if file:
            image_bytes = await file.read()
            gen_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    {"text": text},
                    {
                        "inline_data": {
                            "mime_type": file.content_type,
                            "data": image_bytes
                        }
                    }
                ]
            )
            return JSONResponse({"response": gen_response.text})
        else:
            gen_response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=text
            )
            return JSONResponse({"response": gen_response.text})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

