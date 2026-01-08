from transformers import pipeline
from google import genai
from chunker import overlapping_chunk_by_sentences
import os
from dotenv import load_dotenv
import time

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
        # Measure chunking time
        chunk_start = time.time()
        chunks = overlapping_chunk_by_sentences(text, max_chunk_size=900, overlap_sentences=2)
        chunk_time = time.time() - chunk_start
        
        print(f"\n{'='*50}")
        print(f"TIMING: Chunking completed in {chunk_time:.3f} seconds")
        print(f"Original text length: {len(text)} chars")
        print(f"Split into {len(chunks)} chunks")
        print(f"{'='*50}\n")
        
        if len(chunks) == 1:
            return self._bart_summarize(chunks[0])
        
        try:
            # Use batch processing for faster inference
            result = self._bart_map_reduce_summarize(chunks, use_batch=True)
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

    def _bart_map_reduce_summarize(self, chunks: list, use_batch=True):
        print(f"Processing {len(chunks)} chunks with BART...")
        chunk_summaries = []
        
        # Measure first level summarization time
        first_level_start = time.time()
        
        # Filter empty chunks
        valid_chunks = [(i, chunk) for i, chunk in enumerate(chunks) if len(chunk.strip()) > 0]
        
        if use_batch and len(valid_chunks) > 1:
            # Batch processing - much faster for multiple chunks
            print(f"Using batch processing for {len(valid_chunks)} chunks...")
            try:
                texts = [chunk for _, chunk in valid_chunks]
                max_len = 150
                min_len = 80
                
                # Process all chunks in one batch call
                batch_start = time.time()
                results = self.summarizer(
                    texts, 
                    max_length=max_len, 
                    min_length=min_len, 
                    do_sample=False,
                    batch_size=len(texts)  # Process all at once
                )
                batch_time = time.time() - batch_start
                
                chunk_summaries = [r['summary_text'] for r in results]
                print(f"  Batch processing completed in {batch_time:.3f} seconds")
                print(f"  Average per chunk: {batch_time/len(texts):.3f} seconds")
                
            except Exception as e:
                print(f"Batch processing failed: {str(e)}, falling back to sequential...")
                use_batch = False
        
        if not use_batch or len(valid_chunks) <= 1:
            # Sequential processing (original method)
            for i, chunk in valid_chunks:
                chunk_start = time.time()
                print(f"Summarizing chunk {i+1}/{len(chunks)}...")
                summary = self._bart_summarize(chunk)
                chunk_summaries.append(summary[0]['summary_text'])
                print(f"  Chunk {i+1} took {time.time() - chunk_start:.3f} seconds")
        
        first_level_time = time.time() - first_level_start
        print(f"\n{'='*50}")
        print(f"TIMING: First level summarization (all chunks) completed in {first_level_time:.3f} seconds")
        print(f"{'='*50}\n")
        
        combined = " ".join(chunk_summaries)
        print(f"Combined chunk summaries length: {len(combined)}")
        
        # Measure second level summarization time
        if len(combined) <= 1500:
            print("Creating final summary from combined chunks...")
            second_level_start = time.time()
            final_summary = self._bart_summarize(combined)
            second_level_time = time.time() - second_level_start
            print(f"\n{'='*50}")
            print(f"TIMING: Second level summarization completed in {second_level_time:.3f} seconds")
            print(f"{'='*50}\n")
            return final_summary
        else:
            print("Combined summary too long, truncating...")
            return [{"summary_text": combined[:1000] + "..."}]

    def _gemini_summarize(self, text: str):
        print("Using Gemini for summarization...")
        prompt = f"Summarize the following text in 80-150 words:\n\n{text}"
        response = self.client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=prompt
        )
        return [{"summary_text": response.text}]