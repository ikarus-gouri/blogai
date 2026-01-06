from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix

def extract_keywords(text, top_k=10):
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=500
    )
    tfidf = vectorizer.fit_transform([text])
    tfidf = csr_matrix(tfidf)

    feature_names = vectorizer.get_feature_names_out()
    row = tfidf.tocsr().getrow(0)
    scores = row.data
    indices = row.indices

    ranked = sorted(
        zip(indices, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [feature_names[i] for i, _ in ranked[:top_k]]
