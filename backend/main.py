from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import requests
import pdfplumber
import os
from typing import Optional
import json
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
except:
    pass

app = FastAPI(title="AI Text Summarizer", description="PDF and Text Summarization API using Hugging Face")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://omerkalay.github.io",  # Your GitHub Pages URL
        "https://omerkalay.github.io/text-sum",  # Your repo specific URL
        "http://localhost:3000",  # For local development
        "http://127.0.0.1:5500",  # For VS Code Live Server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hugging Face API configuration
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "your_token_here")

headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    """Extract text content from uploaded PDF file"""
    try:
        with pdfplumber.open(pdf_file.file) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

def summarize_text(text: str, max_length: int = 150) -> str:
    """Summarize text using Hugging Face API"""
    try:
        # Prepare the request payload
        payload = {
            "inputs": text,
            "parameters": {
                "max_length": max_length,
                "min_length": 30,
                "do_sample": False
            }
        }
        
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("summary_text", "Summary generation failed")
            else:
                return result.get("summary_text", "Summary generation failed")
        else:
            raise HTTPException(status_code=500, detail=f"API Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Text Summarizer</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🤖 AI Text Summarizer</h1>
                <p>Upload a PDF or enter text to get an AI-powered summary</p>
            </header>
            
            <div class="tabs">
                <button class="tab-btn active" onclick="switchTab('pdf')">📄 PDF Upload</button>
                <button class="tab-btn" onclick="switchTab('text')">📝 Text Input</button>
            </div>
            
            <div id="pdf-tab" class="tab-content active">
                <form id="pdf-form" enctype="multipart/form-data">
                    <div class="file-upload">
                        <input type="file" id="pdf-file" name="file" accept=".pdf" required>
                        <label for="pdf-file">Choose PDF file</label>
                    </div>
                    <button type="submit" class="submit-btn">Summarize PDF</button>
                </form>
            </div>
            
            <div id="text-tab" class="tab-content">
                <form id="text-form">
                    <textarea id="input-text" name="text" placeholder="Enter your text here..." required></textarea>
                    <div class="options">
                        <label for="max-length">Summary Length:</label>
                        <select id="max-length" name="max_length">
                            <option value="100">Short (100 words)</option>
                            <option value="150" selected>Medium (150 words)</option>
                            <option value="200">Long (200 words)</option>
                        </select>
                    </div>
                    <button type="submit" class="submit-btn">Summarize Text</button>
                </form>
            </div>
            
            <div id="result" class="result-container" style="display: none;">
                <h3>📋 Summary</h3>
                <div id="summary-text" class="summary-text"></div>
                <div class="stats">
                    <span id="original-length"></span>
                    <span id="summary-length"></span>
                </div>
                <button onclick="downloadSummary()" class="download-btn">📥 Download Summary</button>
            </div>
            
            <div id="loading" class="loading" style="display: none;">
                <div class="spinner"></div>
                <p>Generating summary...</p>
            </div>
        </div>
        
        <script src="/static/script.js"></script>
    </body>
    </html>
    """

@app.post("/summarize-pdf")
async def summarize_pdf(file: UploadFile = File(...)):
    """Summarize text extracted from uploaded PDF"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Extract text from PDF
    text = extract_text_from_pdf(file)
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")
    
    # Summarize the extracted text
    summary = summarize_text(text)
    
    return {
        "original_text": text,
        "summary": summary,
        "original_length": len(text.split()),
        "summary_length": len(summary.split())
    }

@app.post("/summarize-text")
async def summarize_text_endpoint(
    text: str = Form(...),
    max_length: int = Form(150)
):
    """Summarize provided text"""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Limit max_length to reasonable bounds
    max_length = max(50, min(500, max_length))
    
    # Summarize the text
    summary = summarize_text(text, max_length)
    
    return {
        "original_text": text,
        "summary": summary,
        "original_length": len(text.split()),
        "summary_length": len(summary.split())
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Text Summarizer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 