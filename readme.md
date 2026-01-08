

# BlogAI Microservice

A production-ready AI microservice for intelligent blog content analysis, providing automated text classification, summarization, and keyword extraction capabilities.

## Overview

BlogAI is a Flask-based REST API that leverages state-of-the-art NLP models to process and analyze blog content. The service is containerized with Docker and optimized for deployment on Hugging Face Spaces.

## Features

### 1. Text Classification
- **Algorithm**: Cosine similarity-based classification using sentence embeddings
- **Model**: all-MiniLM-L6-v2 (SentenceTransformers)
- **Categories**: Technology, Healthcare, Finance, Education
- **Output**: Multiple categories with confidence scores
- **Threshold**: Configurable confidence threshold (default: 0.2)

### 2. Text Summarization
- **Primary Model**: Facebook BART-large-CNN (transformer-based)
- **Chunking Strategy**: Overlapping sentence-based chunking for long texts
- **Max Input**: 1024 tokens per chunk
- **Batch Processing**: Optimized batch inference for multi-chunk summarization
- **Fallback**: Gemini Flash API for texts exceeding 10,000 characters
- **Map-Reduce**: Hierarchical summarization for long documents

### 3. Keyword Extraction
- **Method**: Semantic similarity with uniqueness scoring
- **N-gram Support**: Unigrams, bigrams, and trigrams
- **Filtering**: Stopword removal and frequency analysis
- **Uniqueness Score**: Measures keyword specificity to assigned category
- **Auto-Update**: Optional automatic addition of new keywords to categories

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────────────────────┐
│    Flask API (app.py)       │
│  - CORS enabled             │
│  - JSON request/response    │
└──────┬──────────────────────┘
       │
       ├──► classifier.py      → SentenceTransformer (all-MiniLM-L6-v2)
       │                       → Cosine Similarity Scoring
       │
       ├──► summarizer.py      → BART-large-CNN
       │                       → Gemini Flash (fallback)
       │                       → chunker.py (overlapping chunks)
       │
       └──► keyword_extractor.py → N-gram extraction
                                 → NLTK stopwords
                                 → Semantic uniqueness scoring
```

## API Endpoints

### Health Check
```
GET /
```
**Response:**
```json
{
  "status": "BlogAI API is running"
}
```

### Get Categories
```
GET /api/categories
```
**Response:**
```json
{
  "categories": {
    "Technology": ["artificial intelligence", "machine learning", ...],
    "Healthcare": ["healthcare", "medical", ...],
    "Finance": ["finance", "banking", ...],
    "Education": ["education", "students", ...]
  }
}
```

### Analyze Blog
```
POST /api/blog
```
Performs text classification and summarization.

**Request Body:**
```json
{
  "title": "The Future of AI in Healthcare",
  "content": "Artificial intelligence is revolutionizing healthcare..."
}
```

**Response:**
```json
{
  "success": true,
  "summary": "AI is transforming healthcare through machine learning...",
  "classifications": [
    {
      "category": "Healthcare",
      "confidence": 0.847
    },
    {
      "category": "Technology",
      "confidence": 0.623
    }
  ]
}
```

### Extract Keywords
```
POST /api/extract-keywords
```
Extracts unique keywords for a specific category.

**Request Body:**
```json
{
  "text": "Machine learning and AI are revolutionizing technology",
  "category": "Technology",
  "auto_add": false,
  "min_uniqueness_score": 0.2
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "category": "Technology",
    "new_keywords": [
      {
        "keyword": "machine learning revolutionizing",
        "target_similarity": 0.643,
        "other_max_similarity": 0.217,
        "uniqueness_score": 0.426,
        "is_unique": true
      }
    ],
    "unique_keywords_found": 1,
    "total_keywords_found": 5,
    "total_candidates_analyzed": 9
  }
}
```

### Process and Extract
```
POST /api/process-and-extract
```
Automatically classifies text and extracts keywords for the top category.

**Request Body:**
```json
{
  "text": "Deep learning models are advancing medical diagnosis...",
  "auto_add": false
}
```

**Response:**
```json
{
  "success": true,
  "classifications": [
    {
      "category": "Healthcare",
      "confidence": 0.765
    }
  ],
  "keyword_extraction": {
    "category": "Healthcare",
    "new_keywords": [...],
    "unique_keywords_found": 3
  }
}
```

## Usage Examples

### Python Requests
```python
import requests

BASE_URL = "https://gouriikarus3d-blogai.hf.space"

# Analyze blog content
response = requests.post(
    f"{BASE_URL}/api/blog",
    json={
        "title": "AI in Healthcare",
        "content": "Artificial intelligence is transforming healthcare..."
    },
    timeout=120
)

result = response.json()
print(f"Summary: {result['summary']}")
print(f"Categories: {result['classifications']}")
```

### cURL
```bash
curl -X POST https://gouriikarus3d-blogai.hf.space/api/blog \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Trends 2026",
    "content": "Artificial intelligence continues to evolve..."
  }'
```

### Postman
1. Set method to `POST`
2. Enter URL: `https://gouriikarus3d-blogai.hf.space/api/blog`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "title": "Blog Title",
  "content": "Your blog content here..."
}
```

## Environment Variables

Create a `.env` file for local development:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

For Hugging Face Spaces:
1. Go to your Space settings
2. Navigate to "Variables and secrets"
3. Add secret: `GEMINI_API_KEY` with your API key

**Note**: The Gemini API key is optional and only used as a fallback for very long texts (>10,000 characters).

## Technology Stack

- **Framework**: Flask 3.1.2
- **CORS**: Flask-CORS 6.0.2
- **ML Models**:
  - Transformers 4.57.3 (BART, Sentence-Transformers)
  - PyTorch 2.9.1
  - Sentence-Transformers 5.2.0
- **NLP**: NLTK (stopwords, tokenization)
- **ML Utils**: Scikit-learn 1.5.2
- **Server**: Gunicorn 21.2.0
- **AI API**: Google Generative AI 1.0.0

## Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```
Server runs on `http://localhost:7860`

### Docker
```bash
# Build image
docker build -t blogai .

# Run container
docker run -p 7860:7860 -e GEMINI_API_KEY=your_key blogai
```

### Hugging Face Spaces
1. Create a new Space with Docker SDK
2. Clone repository: `git clone https://huggingface.co/spaces/YOUR_USERNAME/blogai`
3. Add files and push:
```bash
git add .
git commit -m "Deploy BlogAI"
git push
```

## Project Structure

```
blogai/
├── app.py                  # Main Flask application
├── classifier.py           # Text classification module
├── summarizer.py          # Text summarization module
├── keyword_extractor.py   # Keyword extraction module
├── chunker.py             # Text chunking utilities
├── labels.py              # Category definitions
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── README.md             # Documentation
└── .env.example          # Environment variables template
```

## Performance Optimization

- **Batch Processing**: BART model uses batch inference for multi-chunk summarization
- **CPU Optimization**: Models configured for CPU inference with caching disabled
- **Chunking Strategy**: Overlapping sentence-based chunks preserve context
- **Lazy Loading**: Models loaded once at startup
- **Efficient Embeddings**: Pre-computed category embeddings cached in memory

## Error Handling

All endpoints return structured error responses:

```json
{
  "error": "Error message describing what went wrong",
  "success": false
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad request (missing/invalid parameters)
- `500`: Internal server error (model/processing failure)

## License

This project is open source and available for educational and commercial use.

## Deployed Instance

Live API: `https://gouriikarus3d-blogai.hf.space`

## Contact

For issues, feature requests, or contributions, please visit the Hugging Face Space page.
- GET `/api/health` - Health check