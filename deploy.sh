#!/bin/bash

# AI Text Summarizer - GitHub Pages Deployment Script
echo "🚀 AI Text Summarizer - GitHub Pages Deployment"
echo "================================================"

# Check if backend URL is provided
if [ -z "$1" ]; then
    echo "❌ Error: Please provide your backend URL"
    echo "Usage: ./deploy.sh https://your-backend-app.onrender.com"
    exit 1
fi

BACKEND_URL=$1

echo "📝 Backend URL: $BACKEND_URL"
echo ""

# Update script.js with backend URL
echo "🔧 Updating backend URL in script.js..."
sed -i "s|https://your-backend-app.onrender.com|$BACKEND_URL|g" script.js

echo "✅ Backend URL updated successfully!"
echo ""

# Check if files exist
echo "📁 Checking required files..."
if [ ! -f "index.html" ]; then
    echo "❌ Error: index.html not found"
    exit 1
fi

if [ ! -f "style.css" ]; then
    echo "❌ Error: style.css not found"
    exit 1
fi

if [ ! -f "script.js" ]; then
    echo "❌ Error: script.js not found"
    exit 1
fi

echo "✅ All required files found!"
echo ""

# Git setup
echo "🔧 Setting up Git repository..."
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Add files
git add index.html style.css script.js
echo "✅ Files added to Git"

# Commit
git commit -m "Deploy AI Text Summarizer frontend" 2>/dev/null || git commit -m "Update AI Text Summarizer frontend"
echo "✅ Changes committed"

echo ""
echo "🎉 Deployment files ready!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Run: git remote add origin https://github.com/your-username/your-repo-name.git"
echo "3. Run: git push -u origin main"
echo "4. Go to Settings > Pages and enable GitHub Pages"
echo ""
echo "🌐 Your app will be available at: https://your-username.github.io/your-repo-name"
echo ""
echo "💡 Don't forget to update CORS settings in your backend!" 