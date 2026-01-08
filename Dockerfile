FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Expose port 7860 (required by HF Spaces)
EXPOSE 7860

# Run with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "--workers", "1", "--timeout", "300", "api:app"]