from transformers import pipeline
from google import genai
from chunker import overlapping_chunk_by_sentences
import os
from dotenv import load_dotenv

load_dotenv()

class blogsummarizer:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)
        
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None

    def summarize(self, text: str, strategy: str = "auto"):
        text = text.strip()
        if not text:
            raise ValueError("Text cannot be empty")
        
        if len(text) > 10000:
            if self.client:
                return self._gemini_summarize(text)
            else:
                print("Text > 10000 chars but no Gemini API key, using BART chunks...")
        
        if len(text) <= 1024:
            return self._bart_summarize(text)
        else:
            return self._chunked_summarize(text, strategy)

    def _bart_summarize(self, text: str):
        try:
            max_len = min(150, len(text.split()))
            min_len = min(80, max_len - 10)
            result = self.summarizer(text, max_length=max_len, min_length=min_len, do_sample=False)
            return result
        except Exception as e:
            print(f"BART failed: {str(e)}")
            if self.client:
                return self._gemini_summarize(text)
            raise

    def _chunked_summarize(self, text: str, strategy: str):
        chunks = overlapping_chunk_by_sentences(text, max_chunk_size=900, overlap_sentences=2)
        
        print(f"Original text length: {len(text)} chars")
        print(f"Split into {len(chunks)} chunks")
        
        if len(chunks) == 1:
            return self._bart_summarize(chunks[0])
        
        try:
            result = self._bart_map_reduce_summarize(chunks)
            result[0]['metadata'] = {
                'original_length': len(text),
                'num_chunks': len(chunks),
                'chunk_lengths': [len(c) for c in chunks]
            }
            return result
        except Exception as e:
            print(f"BART chunked summarization failed: {str(e)}")
            if self.client:
                print("Falling back to Gemini...")
                return self._gemini_summarize(text)
            raise

    def _bart_map_reduce_summarize(self, chunks: list):
        print(f"Processing {len(chunks)} chunks with BART...")
        chunk_summaries = []
        
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) > 0:
                print(f"Summarizing chunk {i+1}/{len(chunks)}...")
                summary = self._bart_summarize(chunk)
                chunk_summaries.append(summary[0]['summary_text'])
        
        combined = " ".join(chunk_summaries)
        print(f"Combined chunk summaries length: {len(combined)}")
        
        if len(combined) <= 1024:
            print("Creating final summary from combined chunks...")
            return self._bart_summarize(combined)
        else:
            print("Combined summary too long, truncating...")
            return [{"summary_text": combined[:1000] + "..."}]

    def _gemini_summarize(self, text: str):
        print("Using Gemini for summarization...")
        prompt = f"Summarize the following text in 80-150 words:\n\n{text}"
        response = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        return [{"summary_text": response.text}]