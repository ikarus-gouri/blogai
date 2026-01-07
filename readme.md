summarizer:
Facebooks BART Model used as primary summarizer (transformer based model)
max length of blog 1024 thus kept geminai as fallback and to handel larger conten
other solution is chunking though:
types of chunking character chunking might result in context loss due to chunking from middle of the word or sentence
thus using overlapping chunking with . as identifier to chunck sentences as whole and avoid splitting sentences
why not semantic chunking too expensive as already dealing with the BART Model thus to save computation

classifier/ categorizer:
used vertorization
to check the cosine similarity= confidence
based on the cnfidence the blog is categorized

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