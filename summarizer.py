from transformers import pipeline


class blogsummarizer:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)
        
    def summarize(self, text: str):
        result=self.summarizer(text, max_length=150, min_length=80, do_sample=False)
        return result