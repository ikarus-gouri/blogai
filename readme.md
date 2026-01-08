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

AI-powered blog analysis service with:
- Text classification
- Summarization (BART + Gemini fallback)
- Keyword extraction

## API Endpoints
- POST `/api/analyse-blog` - Full analysis
- POST `/api/classify` - Classification only
- POST `/api/summarize` - Summarization only
- GET `/api/health` - Health check