from flask import Flask, request, jsonify
from flask_cors import CORS
from classifier import TextClassifier
# from dynamic_updater import add_keywords_by_similarity, save_categories_to_file, keyword_exists
from labels import CATEGORIES
from summarizer import blogsummarizer
import json

app = Flask(__name__)
CORS(app)

classifier = TextClassifier()
summarizer = blogsummarizer()

@app.route('/api/classify', methods=['POST'])
def classify_text():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        auto_update = data.get('auto_update', False)
        
        result = classifier.classify(text)
        
        if auto_update and result['similar_new_keywords']:
            add_keywords_by_similarity(
                result['similar_new_keywords'],
                result['false_positives']
            )
        
        return jsonify({
            'success': True,
            'classifications': result['classifications']
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
        
        if not text or len(text.strip()) == 0:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        result = summarizer.summarize(text)
        summary = result[0]['summary_text']
        
        return jsonify({
            'success': True,
            'summary': summary,
            'original_length': len(text),
            'used_model': 'Gemini' if len(text) > 1024 else 'BART'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
