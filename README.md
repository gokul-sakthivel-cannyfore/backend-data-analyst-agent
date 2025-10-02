run to start - uvicorn main:app --reload --port 8000
run to set your api key - set GEMINI_API_KEY=YOUR_API_KEY

Gemini AI Text Analysis API
    - A FastAPI-based application that provides text analysis using Google's Gemini AI. The API can process text input, URLs, and images to generate AI-powered responses.

Features
    - Text Analysis: Direct text input processing using Gemini AI
    - URL Content Extraction: Scrape and analyze content from web pages
    - Image Analysis: Process images with optional text prompts using Gemini Vision
    - CORS Enabled: Configured for both local development and GitHub Pages deployment

API Endpoints
### POST `/api/text/`

Analyze text, URL content, or images using Gemini AI.
#### Parameters (form-data):

- `text` (optional): Direct text input for analysis
- `url` (optional): URL to scrape and analyze content from
- `file` (optional): Image file for visual analysis

Examples:
Text Analysis:
```bash
curl -X POST "http://localhost:8000/api/text/" \
  -F "text=Explain the concept of machine learning"