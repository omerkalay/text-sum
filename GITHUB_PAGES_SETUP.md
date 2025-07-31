# 🚀 GitHub Pages + Render.com Deployment Guide

This guide will help you deploy your AI Text Summarizer application with frontend on GitHub Pages and backend on Render.com.

## 📋 Step-by-Step Setup

### 1. Deploy Backend on Render.com

#### 1.1 Create GitHub Repository
```bash
# Create a new repository (e.g., ai-text-summarizer-backend)
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/ai-text-summarizer-backend.git
git push -u origin main
```

#### 1.2 Deploy on Render.com
1. Go to [Render.com](https://render.com)
2. Click "New Web Service"
3. Connect your GitHub repository
4. Configure settings as follows:
   - **Name**: `ai-text-summarizer-backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `HUGGINGFACE_TOKEN`: Your Hugging Face token
6. Click "Create Web Service"

#### 1.3 Note Your Backend URL
After deployment is complete, you'll get a URL in this format:
```
https://ai-text-summarizer-backend.onrender.com
```

### 2. Deploy Frontend on GitHub Pages

#### 2.1 Create New Repository
```bash
# Create a new repository (e.g., ai-text-summarizer-frontend)
mkdir ai-text-summarizer-frontend
cd ai-text-summarizer-frontend
```

#### 2.2 Copy Frontend Files
Copy these files to the new repository:
- `index.html`
- `style.css`
- `script.js`

#### 2.3 Update Backend URL
Find and update this line in `script.js`:
```javascript
const API_BASE_URL = 'https://ai-text-summarizer-backend.onrender.com'; // Your backend URL
```

#### 2.4 Enable GitHub Pages
1. Push repository to GitHub
2. Go to Settings > Pages
3. Source: Select "Deploy from a branch"
4. Branch: Select "main"
5. Folder: Select "/ (root)"
6. Save

### 3. Update CORS Settings

Update CORS settings in the backend `main.py` file:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-username.github.io",  # Your GitHub Pages URL
        "https://your-username.github.io/ai-text-summarizer-frontend",  # If using specific repo
        "http://localhost:3000",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🔧 Security Settings

### Token Security
1. **Never push Hugging Face token to GitHub**
2. Store only in Render.com as environment variable
3. Add `.env` file to `.gitignore`

### CORS Security
- Only add necessary domains to allow_origins
- Don't use wildcard (*) in production

## 📁 Final Project Structure

```
ai-text-summarizer-backend/ (GitHub + Render.com)
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── static/
└── render.yaml

ai-text-summarizer-frontend/ (GitHub Pages)
├── index.html
├── style.css
└── script.js
```

## 🌐 Access URLs

- **Frontend**: `https://your-username.github.io/ai-text-summarizer-frontend`
- **Backend API**: `https://ai-text-summarizer-backend.onrender.com`

## 🧪 Testing

1. Go to frontend URL
2. Upload PDF or enter text
3. Click summarize button
4. Check the result

## 🔍 Troubleshooting

### CORS Error
- Check CORS settings in backend
- Make sure frontend URL is correct

### API Error
- Verify backend URL is correct
- Check if service is running on Render.com

### Token Error
- Verify Hugging Face token is correct
- Check if environment variable is set in Render.com

## 💡 Tips

1. **For development**: Use `http://localhost:8000` for local testing
2. **For production**: Use Render.com URL
3. **For debugging**: Check errors in browser console
4. **For performance**: Host backend in same region

## 🎉 Success!

Your application is now running with:
- ✅ Frontend on GitHub Pages
- ✅ Backend on Render.com
- ✅ Secure token management
- ✅ CORS protection
- ✅ Free hosting 