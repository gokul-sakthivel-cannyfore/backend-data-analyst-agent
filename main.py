from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google import genai
import os
import requests
from bs4 import BeautifulSoup
import uvicorn

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
    text: str = Form(""),                 
    url: str = Form(""),                  
    file: UploadFile = File(None)        
):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables!")

    client = genai.Client(api_key=api_key)

    if not text.strip() and not url.strip() and not file:
        raise HTTPException(status_code=400, detail="Provide text, url, or image")

    try:
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render sets PORT, fallback = 8000 for local
    uvicorn.run("main:app", host="0.0.0.0", port=port)