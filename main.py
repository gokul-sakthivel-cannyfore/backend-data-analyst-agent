from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
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

class TextRequest(BaseModel):
    text: str
class ScrapeRequest(BaseModel):
    url: str

# @app.post("/api/text/")
# async def analyze_text(request: TextRequest):
#     print(request)
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         raise ValueError("GEMINI_API_KEY not found in environment variables!")

#     client = genai.Client(api_key=api_key)

#     if not request.text.strip():
#         raise HTTPException(status_code=400, detail="Text cannot be empty")

#     gen_response = client.models.generate_content(
#         model="gemini-2.0-flash",
#         contents=request.text
#     )
#     print(gen_response)
#     return JSONResponse({"response": gen_response.text})


@app.post("/api/text/")
async def analyze_text(
    text: str = Form(...),
    file: UploadFile = File(None)   # optional image
):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables!")

    client = genai.Client(api_key=api_key)
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        if file:   # ✅ case: text + image
            image_bytes = await file.read()
            gen_response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=([
                {"text": text},
                    {
                        "inline_data": {
                            "mime_type": file.content_type,
                            "data": image_bytes
                        }
                    }
                ])
        )
            # response = model.generate_content([
            #     {"text": text},
            #     {
            #         "inline_data": {
            #             "mime_type": file.content_type,
            #             "data": image_bytes
            #         }
            #     }
            # ])
        else:      # ✅ case: text only
            gen_response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=text
            )

        return JSONResponse({"response": gen_response.text})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/scrape/")
def scrape(request: ScrapeRequest):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/123.0 Safari/537.36"
    }
    try:
        response = requests.get(request.url, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()
        return {"content": text}
    except Exception as e:
        return {"error": str(e)}

