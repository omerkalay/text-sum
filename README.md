# AI Text Summarizer 

A modern web application that leverages AI to generate concise summaries from PDFs and long texts. Built with a Python FastAPI backend and vanilla JavaScript frontend.

## 🌐 Live Demo

**Try it out:** [AI Text Summarizer](https://omerkalay.github.io/text-sum)

## 🚀 Features

- **PDF Processing**: Extract and summarize text from PDF files
- **Smart Length Control**: Optimized single-call system with intelligent parameter tuning
- **AI Summarization**: BART model with dynamic parameters optimized for text complexity
- **Flexible Summary Lengths**: Short, Medium, and Long options adaptive to text complexity
- **Modern UI**: Dark/light theme with smooth animations and user guidance tooltips
- **Drag & Drop**: Easy file upload interface with content warnings
- **Export Options**: Download summaries or copy to clipboard
- **Mobile Responsive**: Works seamlessly on all devices

## 🛠️ Tech Stack

### Frontend
- **Vanilla JavaScript** - No frameworks, pure ES6+
- **Modern CSS** - CSS Variables, animations, responsive design
- **FontAwesome** - Professional icons

### Backend
- **FastAPI** - High-performance Python API
- **pdfplumber** - PDF text extraction
- **Hugging Face API** - AI text summarization
- **CORS & Security** - Production-ready configuration

### Deploy (Render + GitHub Pages)

Backend on Render (Free):

1. Fork/clone repo → connect to Render as Web Service
2. Use the provided `render.yaml` or set:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Env Var: `HUGGINGFACE_TOKEN` (set in dashboard)
   - Health Check Path: `/health`
3. Region: choose closest (ex: `frankfurt`)

Frontend on GitHub Pages:

1. Enable Pages for this repo (root → `index.html`, `script.js`, `style.css`)
2. The app defaults to `https://text-sum-7t11.onrender.com` as backend
3. Override API at runtime if needed:
   - Query param: `?api=https://your-service.onrender.com`
   - Or persist: open console → `localStorage.setItem('apiBaseUrl','https://...')`

Notes for free tiers:

- The backend handles HF model warm-up (503) and rate limits (429) with user-friendly messages.
- Very long texts are chunked and summarized in two passes to fit HF limits.
## 🔧 Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/omerkalay/text-sum.git
cd text-sum
```

2. **Backend setup:**
```bash
cd backend
pip install -r requirements.txt
echo "HUGGINGFACE_TOKEN=your_token_here" > .env
python main.py
```

3. **Frontend:**
```bash
# Open index.html with any web server
# Example: VS Code Live Server, or simply open in browser
```

## 📋 API Endpoints

- `POST /summarize-pdf` - Upload and summarize PDF files
- `POST /summarize-text` - Summarize text input with intelligent length control
- `POST /summarize-youtube` - Summarize YouTube video via transcript (no YouTube API key required)
- `GET /health` - API health check

## 🧠 Advanced AI Features

- **Adaptive Length Control**: AI adjusts summary length based on content complexity and user preference
- **Smart Parameter Tuning**: Automatic optimization of AI model parameters for best results
- **User Guidance System**: Tooltip recommendations for optimal text length ranges
- **Free Tier Optimized**: Efficient single API call designed for reliable performance

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

**Note:** Commercial use requires explicit permission from the author.