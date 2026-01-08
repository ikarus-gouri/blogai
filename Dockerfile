FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data to a specific location
RUN python -m nltk.downloader -d /usr/local/share/nltk_data punkt stopwords averaged_perceptron_tagger

# Copy all application files
COPY . .

# Set NLTK data path
ENV NLTK_DATA=/usr/local/share/nltk_data

# Expose port 7860 (required by HF Spaces)
EXPOSE 7860

# Run with app.py instead of api.py
CMD ["gunicorn", "-b", "0.0.0.0:7860", "--workers", "1", "--timeout", "300", "app:app"]