from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from labels import CATEGORIES
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords

# Download stopwords on first run
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class KeywordExtractor:
    def __init__(self, similarity_threshold=0.4, uniqueness_threshold=0.2):
        self.model = SentenceTransformer("all-MiniLM-L6-v2", device='cpu')
        self.model._modules['0'].auto_model.config.use_cache = False
        self.similarity_threshold = similarity_threshold
        self.uniqueness_threshold = uniqueness_threshold
        self.categories = CATEGORIES.copy()
        self.category_embeddings = self._embed_all_categories()
        self.stopwords = set(stopwords.words('english'))
        
    def _embed_all_categories(self):
        embeddings = {}
        for category, keywords in self.categories.items():
            keyword_embeddings = self.model.encode(keywords, show_progress_bar=False)
            embeddings[category] = keyword_embeddings
        return embeddings
    
    def _preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        words = [w for w in words if w not in self.stopwords and len(w) > 3]
        return words
    
    def _extract_important_words(self, text, top_n=20):
        words = self._preprocess_text(text)
        word_freq = Counter(words)
        most_common = word_freq.most_common(top_n)
        return [word for word, freq in most_common]
    
    def _extract_ngrams(self, text, n=2, top_n=10):
        words = self._preprocess_text(text)
        
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            ngrams.append(ngram)
        
        ngram_freq = Counter(ngrams)
        most_common = ngram_freq.most_common(top_n)
        return [ngram for ngram, freq in most_common]
    
    def _check_uniqueness_to_category(self, keyword, target_category):
        keyword_embedding = self.model.encode([keyword], show_progress_bar=False)
        
        target_embeddings = self.category_embeddings[target_category]
        target_similarities = cosine_similarity(keyword_embedding, target_embeddings)[0]
        max_target_sim = np.max(target_similarities)
        
        other_max_similarities = []
        for category, embeddings in self.category_embeddings.items():
            if category != target_category:
                similarities = cosine_similarity(keyword_embedding, embeddings)[0]
                other_max_similarities.append(np.max(similarities))
        
        if not other_max_similarities:
            return True, max_target_sim, 0.0
        
        max_other_sim = max(other_max_similarities)
        is_unique = (max_target_sim > max_other_sim + self.uniqueness_threshold)
        
        return is_unique, max_target_sim, max_other_sim
    
    def extract_new_keywords(self, text, assigned_category, top_n=20):
        if assigned_category not in self.categories:
            return {
                "error": f"Category '{assigned_category}' not found",
                "new_keywords": []
            }
        
        candidate_words = self._extract_important_words(text, top_n=top_n)
        bigrams = self._extract_ngrams(text, n=2, top_n=15)
        trigrams = self._extract_ngrams(text, n=3, top_n=10)
        
        candidates = list(set(candidate_words + bigrams + trigrams))
        
        existing_keywords = set()
        for keywords in self.categories.values():
            existing_keywords.update([k.lower() for k in keywords])
        
        new_keywords = []
        
        for candidate in candidates:
            if candidate.lower() in existing_keywords:
                continue
            
            is_unique, target_sim, other_sim = self._check_uniqueness_to_category(
                candidate, assigned_category
            )
            
            if target_sim >= self.similarity_threshold:
                new_keywords.append({
                    "keyword": candidate,
                    "target_similarity": round(float(target_sim), 3),
                    "other_max_similarity": round(float(other_sim), 3),
                    "uniqueness_score": round(float(target_sim - other_sim), 3),
                    "is_unique": bool(is_unique)
                })
        
        new_keywords.sort(key=lambda x: x['uniqueness_score'], reverse=True)
        
        return {
            "category": assigned_category,
            "new_keywords": new_keywords[:15],
            "total_candidates_analyzed": len(candidates),
            "unique_keywords_found": len([k for k in new_keywords if k['is_unique']]),
            "total_keywords_found": len(new_keywords)
        }
    
    def add_keywords_to_category(self, category, keywords_list):
        if category not in self.categories:
            return {"error": f"Category '{category}' not found"}
        
        added_keywords = []
        for keyword in keywords_list:
            if keyword not in self.categories[category]:
                self.categories[category].append(keyword)
                added_keywords.append(keyword)
        
        self.category_embeddings = self._embed_all_categories()
        
        return {
            "category": category,
            "added_keywords": added_keywords,
            "total_keywords_now": len(self.categories[category])
        }
    
    def save_updated_categories(self, filepath="labels_updated.py"):
        """Save updated categories back to labels.py file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Auto-generated categories file\n")
            f.write("# Last updated by KeywordExtractor\n\n")
            f.write("CATEGORIES = {\n")
            for category, keywords in self.categories.items():
                f.write(f'    "{category}": [\n')
                for keyword in keywords:
                    # Escape quotes in keywords
                    escaped_keyword = keyword.replace('"', '\\"')
                    f.write(f'        "{escaped_keyword}",\n')
                f.write("    ],\n")
            f.write("}\n")
        
        return {"message": f"Categories saved to {filepath}", "success": True}


def extract_and_update_keywords(text, assigned_category, auto_add=False, 
                                min_uniqueness_score=0.2):
    extractor = KeywordExtractor(
        similarity_threshold=0.4,
        uniqueness_threshold=0.2
    )
    
    result = extractor.extract_new_keywords(text, assigned_category)
    
    if auto_add and result.get("new_keywords"):
        filtered_keywords = [
            kw["keyword"] for kw in result["new_keywords"]
            if kw["uniqueness_score"] >= min_uniqueness_score
        ]
        
        if filtered_keywords:
            add_result = extractor.add_keywords_to_category(
                assigned_category, 
                filtered_keywords
            )
            result["auto_added"] = add_result
            extractor.save_updated_categories()
    
    return result
