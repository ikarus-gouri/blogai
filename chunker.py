import re
from typing import List


def overlapping_chunk_by_sentences(
    text: str,
    max_chunk_size: int = 900,
    overlap_sentences: int = 2
) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s for s in sentences if s.strip()]
    
    if not sentences:
        return []
    
    chunks = []
    current_chunk = []
    current_size = 0
    i = 0
    
    while i < len(sentences):
        sentence = sentences[i]
        sentence_length = len(sentence)
        
        if not current_chunk:
            current_chunk.append(sentence)
            current_size = sentence_length + 1
            i += 1
        elif current_size + sentence_length <= max_chunk_size:
            current_chunk.append(sentence)
            current_size += sentence_length + 1
            i += 1
        else:
            chunks.append(' '.join(current_chunk))
            overlap_start = max(0, len(current_chunk) - overlap_sentences)
            current_chunk = current_chunk[overlap_start:]
            current_size = sum(len(s) + 1 for s in current_chunk) if current_chunk else 0
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def simple_sentence_chunker(
    text: str,
    sentences_per_chunk: int = 5,
    overlap_sentences: int = 1
) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s for s in sentences if s.strip()]
    
    if not sentences:
        return []
    
    chunks = []
    stride = max(1, sentences_per_chunk - overlap_sentences)
    i = 0
    
    while i < len(sentences):
        chunk_sentences = sentences[i:i + sentences_per_chunk]
        chunks.append(' '.join(chunk_sentences))
        i += stride
    
    return chunks
