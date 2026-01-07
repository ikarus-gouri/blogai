# AI Blog Processing Service

## Overview
blog summarization and classification capabilities.

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

required
# Required Django Backend Endpoints

## 1. Save Classification Results
**POST** `/api/classification/save/`
```json
{
  "blog_id": "string",
  "classifications": [
    {"label": "string", "confidence": 0.95}
  ]
}
```

## 2. Save Summary Results
**POST** `/api/summary/save/`
```json
{
  "blog_id": "string",
  "summary": "string",
  "metadata": {}
}
```

## 3. Fetch Blog Content
**GET** `/api/blog/{blog_id}/`
Response:
```json
{
  "id": "string",
  "title": "string",
  "content": "string"
}
```

## 4. Update Blog Status
**PUT** `/api/blog/{blog_id}/status/`
```json
{
  "status": "processing|completed|failed"
}
```

## 5. Save Complete Processing Result
**POST** `/api/blog/process-result/`
```json
{
  "blog_id": "string",
  "classifications": [],
  "summary": "string",
  "metadata": {}
}
```

## 6. Health Check
**GET** `/api/health/`
Response: `{"status": "ok"}`