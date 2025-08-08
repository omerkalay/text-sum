from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import requests
import pdfplumber
import os
from typing import Optional, List
import time
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

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
# Prefer BART for general summarization; allow override via env
BART_MODEL = os.getenv("SUMMARY_MODEL", "facebook/bart-large-cnn")
BART_API_URL = f"https://api-inference.huggingface.co/models/{BART_MODEL}"
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "").strip()

headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"} if HUGGINGFACE_TOKEN else {}

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

def _call_hf_with_retry(inputs: str, params: dict, timeout_seconds: int = 30, total_wait_seconds: int = 120) -> str:
    """Call Hugging Face Inference API with basic retry and model-warmup handling."""
    start_time = time.time()
    backoff_seconds = 2
    while True:
        try:
            response = requests.post(
                BART_API_URL,
                headers=headers,
                json={"inputs": inputs, "parameters": params},
                timeout=timeout_seconds,
            )

            # Model loading on HF returns 503 with estimated_time
            if response.status_code == 503:
                try:
                    data = response.json()
                    estimated = float(data.get("estimated_time", backoff_seconds))
                except Exception:
                    estimated = backoff_seconds
                if time.time() - start_time + estimated > total_wait_seconds:
                    raise HTTPException(status_code=504, detail="Upstream model loading timed out")
                time.sleep(min(estimated, 10))
                continue

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("summary_text", "Summary generation failed")
                if isinstance(result, dict) and "summary_text" in result:
                    return result.get("summary_text", "Summary generation failed")
                # Some models return {"error": "..."}
                if isinstance(result, dict) and "error" in result:
                    raise HTTPException(status_code=502, detail=f"HF error: {result['error']}")
                raise HTTPException(status_code=502, detail="Unexpected HF response format")

            # Handle rate limit / transient errors with backoff
            if response.status_code in (408, 429, 500, 502, 504):
                if time.time() - start_time + backoff_seconds > total_wait_seconds:
                    raise HTTPException(status_code=502, detail=f"HF API error: {response.status_code}")
                time.sleep(backoff_seconds)
                backoff_seconds = min(backoff_seconds * 2, 20)
                continue

            # Other HTTP errors
            raise HTTPException(status_code=502, detail=f"HF API error: {response.status_code}")

        except requests.exceptions.Timeout:
            if time.time() - start_time + backoff_seconds > total_wait_seconds:
                raise HTTPException(status_code=504, detail="HF API timeout")
            time.sleep(backoff_seconds)
            backoff_seconds = min(backoff_seconds * 2, 20)
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")


def _chunk_text_by_words(text: str, max_words_per_chunk: int) -> List[str]:
    words = text.split()
    chunks: List[str] = []
    for i in range(0, len(words), max_words_per_chunk):
        chunk_words = words[i : i + max_words_per_chunk]
        chunks.append(" ".join(chunk_words))
    return chunks


def summarize_text(text: str, target_length: int = 150) -> str:
    """Summarize text using Hugging Face API.

    Optimizations for free tier:
    - deterministic decoding
    - low num_beams
    - basic chunking + second-pass when input is too long
    """
    try:
        text = (text or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="Empty text")

        # Parameter presets
        if target_length == 100:  # Short
            max_length = 250
            min_length = 80
            length_penalty = 1.0
        elif target_length == 150:  # Medium
            max_length = 350
            min_length = 120
            length_penalty = 1.2
        else:  # Long (200)
            max_length = 450
            min_length = 160
            length_penalty = 1.5

        params = {
            "max_length": max_length,
            "min_length": min_length,
            "do_sample": False,
            "length_penalty": length_penalty,
            "num_beams": 2,
            "early_stopping": True,
            "no_repeat_ngram_size": 2,
        }

        # If text is very long, do a simple map-reduce: summarize chunks, then summarize concatenation
        word_count = len(text.split())
        if word_count > 1500:
            # Reasonable chunk size for BART input length
            chunks = _chunk_text_by_words(text, max_words_per_chunk=800)
            partial_summaries: List[str] = []
            for chunk in chunks:
                partial = _call_hf_with_retry(chunk, params)
                partial_summaries.append(partial)
            combined = "\n".join(partial_summaries)
            # Second pass, target roughly requested length
            second_pass_params = {
                "max_length": max_length,
                "min_length": min_length,
                "do_sample": False,
                "length_penalty": length_penalty,
                "num_beams": 2,
                "early_stopping": True,
                "no_repeat_ngram_size": 2,
            }
            return _call_hf_with_retry(combined, second_pass_params)

        # Single-pass
        return _call_hf_with_retry(text, params)

    except HTTPException:
        raise
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
             <li><code>POST /summarize-youtube</code> - Summarize YouTube video via transcript</li>
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
    
    # Use intelligent adaptive summarization with user's target
    summary = summarize_text(text, max_length)
    
    return {
        "original_text": text,
        "summary": summary,
        "original_length": len(text.split()),
        "summary_length": len(summary.split())
    }


def _extract_youtube_video_id(url: str) -> Optional[str]:
    try:
        # Support youtu.be/<id>, youtube.com/watch?v=<id>, and variants
        if "youtu.be/" in url:
            return url.split("youtu.be/")[-1].split("?")[0]
        if "watch?v=" in url:
            return url.split("watch?v=")[-1].split("&")[0]
        if "/shorts/" in url:
            return url.split("/shorts/")[-1].split("?")[0]
        return None
    except Exception:
        return None


@app.post("/summarize-youtube")
async def summarize_youtube(url: str = Form(...), max_length: int = Form(150)):
    """Summarize a YouTube video by fetching its transcript (no YouTube API key required)."""
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty")

    video_id = _extract_youtube_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    try:
        # Try Turkish or English first, then any
        preferred_langs = ["tr", "en"]
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for lang in preferred_langs:
                if transcript_list.find_transcript([lang]):
                    transcript = transcript_list.find_transcript([lang]).fetch()
                    break
            else:
                transcript = transcript_list.find_transcript(transcript_list._manually_created_transcripts.keys() or ["en"]).fetch()
        except Exception:
            # Fallback to API convenience method
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=preferred_langs)

        text = " ".join(item.get("text", "") for item in transcript if item.get("text"))
        text = text.strip()
        if not text:
            raise HTTPException(status_code=404, detail="Transcript is empty")

        summary = summarize_text(text, max_length)
        return {
            "original_text": text,
            "summary": summary,
            "original_length": len(text.split()),
            "summary_length": len(summary.split()),
            "video_id": video_id,
        }

    except TranscriptsDisabled:
        raise HTTPException(status_code=403, detail="Transcripts are disabled for this video")
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="No transcript found for this video")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube transcript error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Text Summarizer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 