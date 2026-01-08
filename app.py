from flask import Flask, request, jsonify
from flask_cors import CORS
from classifier import TextClassifier
from labels import CATEGORIES
from summarizer import blogsummarizer
from keyword_extractor import KeywordExtractor, extract_and_update_keywords
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

classifier = TextClassifier()
summarizer = blogsummarizer()

@app.route("/", methods=["GET"])
def health():
    return {"status": "BlogAI API is running"}, 200

@app.route("/api/categories", methods=["GET"])
def get_categories():
    return jsonify({"categories": CATEGORIES}), 200

@app.route('/api/blog', methods=['POST'])
def analyse_blog():
    try: 
        data= request.get_json()
        if not data:
            return jsonify({'error':"invalid json"}),400
        
        title=data.get('title')
        text=data.get('content')
        if not text:
            return jsonify({'error':'content field is required'}),400

        categories=classifier.classify(text)

        summary_result=summarizer.summarize(text)
        summary=summary_result[0].get('summary_text')

        return jsonify({
            'success':True,
            'summary':summary,
            'classifications':categories
        }),200

    except Exception as e:
        return jsonify({'error':str(e)}),500



@app.route('/api/extract-keywords', methods=['POST'])
def extract_keywords():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data or 'category' not in data:
            return jsonify({'error': 'Text and category required'}), 400
        
        text = data['text']
        category = data['category']
        auto_add = data.get('auto_add', False)
        min_uniqueness = data.get('min_uniqueness_score', 0.2)
        
        result = extract_and_update_keywords(
            text, 
            category, 
            auto_add=auto_add,
            min_uniqueness_score=min_uniqueness
        )
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/process-and-extract', methods=['POST'])
def process_and_extract():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        auto_add = data.get('auto_add', False)
        
        classifications = classifier.classify(text)
        
        if not classifications:
            return jsonify({'error': 'No category classified'}), 400
        
        top_category = classifications[0]['category']
        
        keyword_result = extract_and_update_keywords(
            text,
            top_category,
            auto_add=auto_add
        )
        
        return jsonify({
            'success': True,
            'classifications': classifications,
            'keyword_extraction': keyword_result
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7860)

