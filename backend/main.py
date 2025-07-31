from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://omerkalay.github.io",  # GitHub Pages URL
        "https://omerkalay.com",        # Custom domain
        "https://www.omerkalay.com",    # Custom domain with www
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hugging Face API configuration
# Using a better summarization model
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
BART_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
PEGASUS_API_URL = "https://api-inference.huggingface.co/models/google/pegasus-xsum"
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
        # Calculate text metrics for better min_length
        text_word_count = len(text.split())
        
        # Dynamic min_length based on text size and target length
        if text_word_count <= 1500:  # Short text
            min_length = max(50, max_length // 3)  # More conservative for short texts
        elif text_word_count <= 3000:  # Medium text
            min_length = max(80, max_length // 2)  # Standard approach
        else:  # Long text
            min_length = max(100, max_length // 2)  # Higher minimum for long texts
        
        payload = {
            "inputs": text,
            "parameters": {
                "max_length": max_length,
                "min_length": min_length,
                "do_sample": True,  # Enable sampling for more variety
                "length_penalty": 2.0,  # Strong penalty for short summaries
                "num_beams": 4,  # Use beam search for better quality
                "early_stopping": True,
                "no_repeat_ngram_size": 3
            }
        }
        
        response = requests.post(BART_API_URL, headers=headers, json=payload)
        
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
    """API root endpoint"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Text Summarizer API</title>
        <style>
            body { 
                font-family: system-ui; 
                max-width: 800px; 
                margin: 40px auto; 
                padding: 0 20px; 
                line-height: 1.6;
                background: #1a1a1a;
                color: #ffffff;
            }
            pre { 
                background: #2a2a2a; 
                padding: 15px; 
                border-radius: 5px; 
                overflow-x: auto;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            code { 
                background: #2a2a2a; 
                padding: 2px 5px; 
                border-radius: 3px;
                color: #00d4ff;
            }
            a {
                color: #00d4ff;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>🤖 AI Text Summarizer API</h1>
        <p>This is the API server for the AI Text Summarizer. The frontend is hosted at <a href="https://omerkalay.github.io/text-sum">https://omerkalay.github.io/text-sum</a></p>
        
        <h2>API Endpoints:</h2>
        <ul>
            <li><code>POST /summarize-text</code> - Summarize text input</li>
            <li><code>POST /summarize-pdf</code> - Summarize PDF file</li>
            <li><code>GET /health</code> - Health check endpoint</li>
        </ul>
        
        <h2>Example Usage:</h2>
        <pre>
// Summarize Text
fetch('https://text-sum-7t1f.onrender.com/summarize-text', {
    method: 'POST',
    body: new FormData({
        text: 'Your long text here...',
        max_length: 150
    })
})

// Summarize PDF
const formData = new FormData();
formData.append('file', pdfFile);
fetch('https://text-sum-7t1f.onrender.com/summarize-pdf', {
    method: 'POST',
    body: formData
})</pre>
        
        <p>For more information, visit the <a href="https://github.com/omerkalay/text-sum">GitHub repository</a>.</p>
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
    
    # Dynamic length calculation based on text size and user selection
    text_word_count = len(text.split())
    
    # Adjust max_length based on text length and tooltip recommendations
    if text_word_count <= 1500:  # Short text range
        if max_length >= 150:  # User selected Medium/Long but text is short
            max_length = max(max_length * 2, 200)  # More conservative boost
        else:
            max_length = max_length * 2  # Short selection, appropriate boost
    elif text_word_count <= 3000:  # Medium text range  
        max_length = max_length * 2.5  # Standard boost
    else:  # Long text (3000+ words)
        max_length = max_length * 3  # Full boost for long texts
    
    # Final bounds check
    max_length = max(100, min(1000, max_length))
    
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