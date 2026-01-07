from flask import Flask, request, jsonify
from flask_cors import CORS
from classifier import TextClassifier
# from dynamic_updater import add_keywords_by_similarity, save_categories_to_file, keyword_exists
from labels import CATEGORIES
from summarizer import blogsummarizer
from services import DjangoBackendService
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

classifier = TextClassifier()
summarizer = blogsummarizer()

# Initialize Django backend service
DJANGO_BACKEND_URL = os.getenv("DJANGO_BACKEND_URL", "http://localhost:8000")
backend_service = DjangoBackendService(base_url=DJANGO_BACKEND_URL)

@app.route('/api/classify', methods=['POST'])
def classify_text():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        
        result = classifier.classify(text)
        
        return jsonify({
            'success': True,
            'classifications': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Blog Classification API'
    }), 200

@app.route('/api/summarize', methods=['POST'])
def summarize_text():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        strategy = data.get('strategy', 'auto')
        
        if not text or len(text.strip()) == 0:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        result = summarizer.summarize(text, strategy=strategy)
        summary = result[0]['summary_text']
        
        response_data = {
            'success': True,
            'summary': summary,
            'strategy_used': strategy,
            'original_length': len(text),
            'summary_length': len(summary)
        }
        
        if 'metadata' in result[0]:
            response_data['chunk_info'] = result[0]['metadata']
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/summarize-chunked', methods=['POST'])
def summarize_chunked():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        strategy = data.get('strategy', 'auto')
        
        if len(text) <= 1024:
            return jsonify({
                'error': 'Text is too short for chunked summarization. Use /api/summarize instead'
            }), 400
        
        result = summarizer._chunked_summarize(text, strategy)
        summary = result[0]['summary_text']
        
        response_data = {
            'success': True,
            'summary': summary,
            'strategy_used': strategy,
            'original_length': len(text),
            'summary_length': len(summary),
            'method': 'chunked'
        }
        
        if 'metadata' in result[0]:
            response_data['chunk_info'] = result[0]['metadata']
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/process-blog', methods=['POST'])
def process_blog():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        blog_id = data.get('blog_id')
        send_to_backend = data.get('send_to_backend', False)
        strategy = data.get('strategy', 'auto')
        
        if not text or len(text.strip()) == 0:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        classifications = classifier.classify(text)
        summary_result = summarizer.summarize(text, strategy=strategy)
        summary = summary_result[0]['summary_text']
        
        response_data = {
            'success': True,
            'classifications': classifications,
            'summary': summary,
            'metadata': {
                'original_length': len(text),
                'summary_length': len(summary),
                'strategy_used': strategy,
                'num_categories': len(classifications)
            }
        }
        
        if 'metadata' in summary_result[0]:
            response_data['metadata']['chunk_info'] = summary_result[0]['metadata']
        
        if send_to_backend and blog_id:
            try:
                backend_service.update_blog_status(blog_id, "processing")
                backend_response = backend_service.send_processing_result(
                    blog_id=blog_id,
                    classifications=classifications,
                    summary=summary,
                    metadata=response_data['metadata']
                )
                backend_service.update_blog_status(blog_id, "completed")
                response_data['backend_response'] = backend_response
            except Exception as backend_error:
                backend_service.update_blog_status(blog_id, "failed")
                response_data['backend_error'] = str(backend_error)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/fetch-and-process', methods=['POST'])
def fetch_and_process():
    try:
        data = request.get_json()
        
        if not data or 'blog_id' not in data:
            return jsonify({'error': 'blog_id field is required'}), 400
        
        blog_id = data['blog_id']
        strategy = data.get('strategy', 'auto')
        
        blog_data = backend_service.fetch_blog_content(blog_id)
        text = blog_data.get('content', '')
        
        if not text:
            return jsonify({'error': 'No content found in blog'}), 400
        
        backend_service.update_blog_status(blog_id, "processing")
        
        classifications = classifier.classify(text)
        summary_result = summarizer.summarize(text, strategy=strategy)
        summary = summary_result[0]['summary_text']
        
        metadata = {
            'original_length': len(text),
            'summary_length': len(summary),
            'strategy_used': strategy,
            'num_categories': len(classifications)
        }
        
        backend_response = backend_service.send_processing_result(
            blog_id=blog_id,
            classifications=classifications,
            summary=summary,
            metadata=metadata
        )
        
        backend_service.update_blog_status(blog_id, "completed")
        
        return jsonify({
            'success': True,
            'blog_id': blog_id,
            'classifications': classifications,
            'summary': summary,
            'metadata': metadata,
            'backend_response': backend_response
        }), 200
        
    except Exception as e:
        try:
            if 'blog_id' in locals():
                backend_service.update_blog_status(blog_id, "failed")
        except:
            pass
        
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/backend-health', methods=['GET'])
def check_backend_health():
    try:
        health = backend_service.health_check()
        return jsonify({'success': True, 'backend_health': health}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 503


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
