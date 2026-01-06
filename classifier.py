from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from labels import CATEGORIES
from update_dynamically import find_new_keywords, vectorize_keywords, check_similarity, update_category

class TextClassifier:
    def __init__(self, threshold=0.15):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.threshold = threshold
        self.category_embeddings = self._embed_categories()

    def _embed_categories(self):
        embeddings = {}
        for category, keywords in CATEGORIES.items():
            if keywords:
                emb = self.model.encode(keywords)
                embeddings[category] = np.array(emb)
            else:
                dim= int(self.model.get_sentence_embedding_dimension())
                embeddings[category] = np.zeros((0, dim))
        return embeddings

    def classify(self, text: str):
        text_embedding = self.model.encode(text).reshape(1, -1)
        results = {}

        # check similarity with existing category embeddings
        for category, emb in self.category_embeddings.items():
            if len(emb) == 0:
                continue
            scores = cosine_similarity(text_embedding, emb)[0]
            confidence = float(np.max(scores))
            if confidence >= self.threshold:
                results[category] = round(confidence, 3)

        # detect new keywords
        from keywordextractor import extract_keywords
        keywords = extract_keywords(text, top_k=5)
        new_keywords = find_new_keywords(keywords)

        if new_keywords:
            # vectorize and assign to closest category
            new_emb = vectorize_keywords(new_keywords)
            assigned = check_similarity(new_emb, self.category_embeddings, self.threshold)
            for cat in assigned:
                update_category(new_keywords, category=cat)
                if cat not in results:
                    results[cat] = round(assigned[cat], 3)

            if not assigned:
                update_category(new_keywords, category="Uncategorized")
                if "Uncategorized" not in results:
                    results["Uncategorized"] = 1.0

        if not results:
            results["Uncategorized"] = 1.0

        return results
