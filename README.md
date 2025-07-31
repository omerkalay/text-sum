# AI Text Summarizer 🤖

A modern web application that leverages AI to generate concise summaries from PDFs and long texts. Built with a Python FastAPI backend and vanilla JavaScript frontend.

## 🚀 Features

- **PDF Processing**: Extract and summarize text from PDF files using `pdfplumber`
- **Text Summarization**: AI-powered text summarization using Hugging Face models
- **Modern UI**: Responsive design with dark theme and modern animations
- **Drag & Drop**: Easy file upload with drag and drop support
- **Real-time Processing**: Asynchronous API calls with loading states
- **Download Options**: Export summaries as text files

## 🛠️ Architecture

### Frontend
- **Pure JavaScript** (No frameworks)
- Modern ES6+ features
- Responsive CSS with CSS Variables
- FontAwesome icons
- Drag & Drop API
- Fetch API for backend communication

### Backend
- **FastAPI** framework for high-performance API
- **pdfplumber** for PDF text extraction
- **Hugging Face API** integration for AI models
- CORS middleware for security
- Environment variables for configuration
- Async/await for non-blocking operations

## 🔧 Development Setup

1. Clone and install dependencies:
```bash
git clone https://github.com/omerkalay/text-sum.git
cd text-sum/backend
pip install -r requirements.txt
```

2. Configure environment:
```bash
# backend/.env
HUGGINGFACE_TOKEN=your_token_here
```

3. Run development servers:
```bash
# Backend (from backend directory)
python main.py

# Frontend (use any static server, e.g., VS Code Live Server)
# Open frontend/index.html
```

## 📝 Implementation Details

### Backend API Endpoints
- `POST /summarize-pdf`: Handles PDF file uploads
- `POST /summarize-text`: Processes raw text input
- `GET /health`: API health check endpoint

### Security Features
- CORS protection
- Environment variables for sensitive data
- File type validation
- Request size limits
- Error handling

### Deployment
- Frontend: Static hosting (GitHub Pages)
- Backend: Python hosting (Render.com)
- Separate frontend/backend for scalability

## 🌐 Live Demo

Try it out: [AI Text Summarizer](https://omerkalay.github.io/text-sum)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.