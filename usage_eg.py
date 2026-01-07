from classifier import TextClassifier
from summarizer import blogsummarizer
from services import DjangoBackendService
import os
from dotenv import load_dotenv

load_dotenv()

classifier = TextClassifier()
summarizer = blogsummarizer()

DJANGO_BACKEND_URL = os.getenv("DJANGO_BACKEND_URL", "http://localhost:8000")
backend_service = DjangoBackendService(base_url=DJANGO_BACKEND_URL)


def process_blog_complete(blog_id: str, text: str):
    try:
        backend_service.update_blog_status(blog_id, "processing")
        
        classifications = classifier.classify(text)
        print(f"Classifications: {classifications}")
        
        summary_result = summarizer.summarize(text)
        summary = summary_result[0]['summary_text']
        print(f"Summary: {summary}")
        
        metadata = {
            "original_length": len(text),
            "summary_length": len(summary),
            "model_used": "Gemini" if len(text) > 1024 else "BART",
            "num_categories": len(classifications)
        }
        
        response = backend_service.send_processing_result(
            blog_id=blog_id,
            classifications=classifications,
            summary=summary,
            metadata=metadata
        )
        
        backend_service.update_blog_status(blog_id, "completed")
        print(f"Successfully processed blog {blog_id}")
        return response
        
    except Exception as e:
        print(f"Error processing blog {blog_id}: {str(e)}")
        try:
            backend_service.update_blog_status(blog_id, "failed")
        except:
            pass
        raise


def process_blog_from_backend(blog_id: str):
    try:
        blog_data = backend_service.fetch_blog_content(blog_id)
        text = blog_data.get('content', '')
        
        if not text:
            raise ValueError("No content found in blog")
        
        return process_blog_complete(blog_id, text)
        
    except Exception as e:
        print(f"Error fetching and processing blog {blog_id}: {str(e)}")
        raise


def classify_and_send(blog_id: str, text: str):
    classifications = classifier.classify(text)
    response = backend_service.send_classification_result(blog_id, classifications)
    return response


def summarize_and_send(blog_id: str, text: str):
    summary_result = summarizer.summarize(text)
    summary = summary_result[0]['summary_text']
    
    metadata = {
        "original_length": len(text),
        "model_used": "Gemini" if len(text) > 1024 else "BART"
    }
    
    response = backend_service.send_summary_result(blog_id, summary, metadata)
    return response


def check_backend_health():
    try:
        health = backend_service.health_check()
        print(f"Backend health: {health}")
        return True
    except Exception as e:
        print(f"Backend health check failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("=== Checking Backend Health ===")
    check_backend_health()
