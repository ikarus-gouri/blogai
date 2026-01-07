from chunker import overlapping_chunk_by_sentences


def test_overlapping_chunk():
    print("="*80)
    print("TEST: Overlapping Chunk for BART (max_chunk_size=900)")
    print("="*80)
    
    text = """
    Why Write Chunking Strategies for RAG From Scratch?
In the rapidly evolving AI ecosystem, libraries like LangChain have made it incredibly easy to build Retrieval-Augmented Generation (RAG) pipelines. With just a few lines of code, you can ingest documents, chunk them into smaller pieces, and query them using language models to generate contextualized answers. But while these abstractions offer speed and convenience, they can come at a cost.

Become a member
Writing your own chunking logic from scratch might seem like unnecessary work at first — but it unlocks a level of flexibility, control, and understanding that high-level libraries often obscure. By building your chunking functions manually, you gain several key advantages:

Tailored behavior for your specific use case, whether you need to chunk by token count, semantic boundaries, logical sections, or custom metadata.
Freedom from third-party dependencies, making your codebase more portable, maintainable, and future-proof.
Performance and efficiency optimizations, since you eliminate layers of abstraction and have full visibility into every step of the pipeline.
Deeper understanding of how retrieval and generation actually work, which is essential for debugging, auditing, and improving your system.
Implementing chunking from scratch isn’t just a technical exercise — it’s an investment in building a more robust, transparent, and adaptable RAG system that fits your exact needs.
    """
    
    
    print("\nText length:", len(text), "characters")
    
    # Test with chunk_size=900 for BART model (max 1024 tokens)
    print("\n" + "-"*80)
    print("Chunking with max_chunk_size=900, overlap_sentences=2")
    print("-"*80)
    chunks = overlapping_chunk_by_sentences(text, max_chunk_size=900, overlap_sentences=2)
    
    print(f"\nTotal chunks created: {len(chunks)}")
    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i} (length: {len(chunk)} chars):")
        print(f"  {chunk[:150]}..." if len(chunk) > 150 else f"  {chunk}")
    
    print("\n" + "="*80)





def test_edge_cases():
    print("\n\n" + "="*80)
    print("TEST 3: Edge Cases")
    print("="*80)
    
    # Test with single sentence
    print("\nTest: Single Sentence")
    text1 = "This is a single sentence."
    chunks1 = overlapping_chunk_by_sentences(text1, max_chunk_size=100, overlap_sentences=1)
    print(f"Input: {text1}")
    print(f"Output: {chunks1}")
    print(f"Number of chunks: {len(chunks1)}")
    
    # Test with empty text
    print("\nTest: Empty Text")
    text2 = ""
    chunks2 = overlapping_chunk_by_sentences(text2, max_chunk_size=100, overlap_sentences=1)
    print(f"Input: '{text2}'")
    print(f"Output: {chunks2}")
    print(f"Number of chunks: {len(chunks2)}")
    
    # Test with very long sentence
    print("\nTest: Very Long Sentence")
    text3 = "This is a very long sentence that exceeds the maximum chunk size to test how the function handles sentences longer than the specified maximum chunk size parameter value."
    chunks3 = overlapping_chunk_by_sentences(text3, max_chunk_size=50, overlap_sentences=1)
    print(f"Input length: {len(text3)} characters")
    print(f"Output: {chunks3}")
    print(f"Number of chunks: {len(chunks3)}")


def test_with_blog_file():
    print("\n" + "="*80)
    print("TEST: Real Blog File")
    print("="*80)
    
    try:
        with open("blog.txt", "r", encoding="utf-8") as f:
            blog_text = f.read()
        
        print(f"Blog text length: {len(blog_text)} chars")
        
        chunks = overlapping_chunk_by_sentences(blog_text, max_chunk_size=900, overlap_sentences=2)
        
        print(f"Total chunks: {len(chunks)}\n")
        
        for i, chunk in enumerate(chunks[:3], 1):
            preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
            print(f"Chunk {i} ({len(chunk)} chars): {preview}")
        
    except FileNotFoundError:
        print("blog.txt not found. Skipping test.")


if __name__ == "__main__":
    test_overlapping_chunk()
    test_with_blog_file()
    print("\n" + "="*80)
    print("TESTS COMPLETED")
    print("="*80)
