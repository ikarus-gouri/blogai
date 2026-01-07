from sentence_transformers import SentenceTransformer

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from labels import CATEGORIES


class TextClassifier:
    def __init__(self, threshold=0.2):
        self.model=SentenceTransformer("all-MiniLM-L6-v2")
        self.threshold = threshold
        self.category_embeddings = self._embed_categories()
        
    def _embed_categories(self):
        embeddings={}
        for category, keywords in CATEGORIES.items():
            # Encode each keyword separately and stack them
            emb_list = [self.model.encode(keyword) for keyword in keywords]
            embeddings[category]=np.array(emb_list)
        return embeddings
    
    def classify(self, text:str):
        text_embedding= self.model.encode(text)
        text_embedding=np.array(text_embedding).reshape(1,-1)
        results=[]
        
        for category, embeddings in self.category_embeddings.items():
            scores=cosine_similarity(text_embedding, embeddings)[0]
            print(scores)
            confidence=float(np.max(scores))
            print(confidence, category)
            if confidence>= self.threshold:
                results.append({
                    "category":category,
                    "confidence": round(confidence,3)
                    })
        return results
            
 
 