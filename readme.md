---
title: BlogAI Microservice
emoji: 📝
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

# BlogAI Microservice

AI-powered blog analysis service providing intelligent text processing capabilities.

## Features

### Summarizer
- **Primary Model**: Facebook's BART (transformer-based)
- **Max Input**: 1024 tokens
- **Fallback**: Gemini AI for larger content
- **Chunking Strategy**: Overlapping sentence chunking to preserve context
- Avoids character chunking to prevent context loss
- No semantic chunking to reduce computational overhead

### Classifier
- **Method**: Cosine similarity with vectorization
- **Output**: Categories with confidence scores

### Keyword Extraction
- Automated keyword extraction from blog content

## API Endpoints
- `POST /api/analyse-blog` - Full analysis (classification + summarization + keywords)
- `POST /api/classify` - Classification only
- `POST /api/summarize` - Summarization only

## Usage

Send POST requests with JSON body:
```json
{
  "title": "Blog Title",
  "content": "Your blog content here..."
}
```

## Technology Stack
- Flask web framework
- Transformers (BART, Sentence-Transformers)
- PyTorch
- Scikit-learn
- GET `/api/health` - Health check