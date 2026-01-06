from labels import CATEGORIES
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def find_new_keywords(keywords):
    new_keywords = []
    for kw in keywords:
        found = any(kw in kws for kws in CATEGORIES.values())
        if not found:
            new_keywords.append(kw)
    return new_keywords

def vectorize_keywords(keywords):
    if not keywords:
        return np.array([]).reshape(0, model.get_sentence_embedding_dimension())
    return model.encode(keywords)

def check_similarity(new_embeddings, category_embeddings, threshold=0.4):
    """
    new_embeddings: np.array of shape (n_new_keywords, dim)
    category_embeddings: dict {category: np.array of shape (n_keywords, dim)}
    """
    results = {}
    for category, emb in category_embeddings.items():
        if len(new_embeddings) == 0 or len(emb) == 0:
            continue
        scores = cosine_similarity(new_embeddings, emb)
        max_scores = scores.max(axis=1)
        if any(max_scores >= threshold):
            results[category] = float(max_scores.max())
    return results

def update_category(new_keywords, category=None):
    if not new_keywords:
        return
    if category is None:
        category = "Uncategorized"
        if category not in CATEGORIES:
            CATEGORIES[category] = []
    if category not in CATEGORIES:
        CATEGORIES[category] = []
    CATEGORIES[category].extend(new_keywords)
