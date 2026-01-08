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
keyword_extractor = KeywordExtractor()

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



@app.route('/api/keywords/extract', methods=['POST'])
def extract_new_keywords():
    """
    Extract new keywords from blog content and optionally add them to labels.py
    
    Request body:
    {
        "title": "Blog Title",
        "content": "Full blog content...",
        "category": "Technology",
        "confidence": 0.85,
        "auto_add": true,
        "min_uniqueness_score": 0.2
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        content = data.get('content')
        category = data.get('category')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        if not category:
            return jsonify({'error': 'Category is required'}), 400
        
        if category not in CATEGORIES:
            return jsonify({'error': f'Invalid category: {category}'}), 400
        
        # Optional parameters
        auto_add = data.get('auto_add', False)
        min_uniqueness_score = data.get('min_uniqueness_score', 0.2)
        confidence = data.get('confidence', 0.0)
        title = data.get('title', '')
        
        # Extract keywords
        result = keyword_extractor.extract_new_keywords(content, category, top_n=20)
        
        # Auto-add keywords if requested
        added_keywords = []
        if auto_add and result.get("new_keywords"):
            # Filter by uniqueness score
            keywords_to_add = [
                kw["keyword"] for kw in result["new_keywords"]
                if kw["uniqueness_score"] >= min_uniqueness_score and kw["is_unique"]
            ]
            
            if keywords_to_add:
                # Add to category
                add_result = keyword_extractor.add_keywords_to_category(
                    category, 
                    keywords_to_add
                )
                added_keywords = add_result.get('added_keywords', [])
                
                # Save to labels.py
                save_result = keyword_extractor.save_updated_categories(filepath="labels.py")
                
                # Reload CATEGORIES in memory
                import importlib
                import labels
                importlib.reload(labels)
                from labels import CATEGORIES as UPDATED_CATEGORIES
                
                result['keywords_added'] = {
                    'count': len(added_keywords),
                    'keywords': added_keywords,
                    'total_keywords_now': len(UPDATED_CATEGORIES[category]),
                    'saved_to_file': True
                }
        
        return jsonify({
            'success': True,
            'category': category,
            'confidence': confidence,
            'title': title,
            'extraction_result': {
                'new_keywords_found': result.get('new_keywords', []),
                'total_candidates_analyzed': result.get('total_candidates_analyzed', 0),
                'unique_keywords_found': result.get('unique_keywords_found', 0)
            },
            'keywords_added': result.get('keywords_added', {
                'count': 0,
                'keywords': [],
                'saved_to_file': False
            })
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/keywords/add', methods=['POST'])
def add_keywords_manually():
    """
    Manually add keywords to a category
    
    Request body:
    {
        "category": "Technology",
        "keywords": ["machine learning", "artificial intelligence"]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        category = data.get('category')
        keywords = data.get('keywords', [])
        
        if not category or not keywords:
            return jsonify({'error': 'Category and keywords are required'}), 400
        
        if category not in CATEGORIES:
            return jsonify({'error': f'Invalid category: {category}'}), 400
        
        # Add keywords
        add_result = keyword_extractor.add_keywords_to_category(category, keywords)
        
        # Save to labels.py
        keyword_extractor.save_updated_categories(filepath="labels.py")
        
        return jsonify({
            'success': True,
            'result': add_result
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

