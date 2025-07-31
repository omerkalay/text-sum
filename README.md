# AI Text Summarizer 

A modern web application that leverages AI to generate concise summaries from PDFs and long texts. Built with a Python FastAPI backend and vanilla JavaScript frontend.

## 🌐 Live Demo

**Try it out:** [AI Text Summarizer](https://omerkalay.github.io/text-sum)

## 🚀 Features

- **PDF Processing**: Extract and summarize text from PDF files
- **Text Summarization**: AI-powered summarization using Hugging Face BART model
- **Modern UI**: Dark/light theme with smooth animations
- **Drag & Drop**: Easy file upload interface
- **Smart Controls**: Adjustable summary length, character counter
- **Export Options**: Download summaries or copy to clipboard
- **Mobile Responsive**: Works on all devices

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
- `POST /summarize-text` - Summarize text input
- `GET /health` - API health check

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.