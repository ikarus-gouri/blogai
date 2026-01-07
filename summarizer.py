from transformers import pipeline
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

load_dotenv()

class blogsummarizer:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)

        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-3-flash-preview')
        else:
            self.gemini_model = None

    
    def summarize(self, text: str):
        if len(text) > 1024:
            if self.gemini_model:
                try:
                    prompt = f"Summarize the following text in 80-150 words:\n\n{text}"
                    response = self.gemini_model.generate_content(prompt)
                    return [{"summary_text": response.text}]
                except Exception as gemini_error:
                    print(f"Gemini summarization failed: {str(gemini_error)}")
                    raise Exception("Gemini summarization failed for long text")
            else:
                raise Exception("Text exceeds 1024 characters but Gemini API key not configured")
        
        try:
            
            result = self.summarizer(text, max_length=min(150,len(text)), min_length=min(80,len(text)), do_sample=False)
            return result
        except Exception as e:
            print(f"BART model failed: {str(e)}")
            
            if self.gemini_model:
                try:
                    prompt = f"Summarize the following text in 80-150 words:\n\n{text}"
                    response = self.gemini_model.generate_content(prompt)
                    return [{"summary_text": response.text}]
                except Exception as gemini_error:
                    print(f"Gemini fallback also failed: {str(gemini_error)}")
                    raise Exception("Both BART and Gemini summarization failed")
            else:
                raise Exception("BART failed and Gemini API key not configured")