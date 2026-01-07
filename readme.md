summarizer:
Facebooks BART Model used as primary summarizer (transformer based model)
max length of blog 1024 thus kept geminai as fallback and to handel larger conten
other solution is chunking though:
types of chunking character chunking might result in context loss due to chunking from middle of the word or sentence
thus using overlapping chunking with . as identifier to chunck sentences as whole and avoid splitting sentences
why not semantic chunking too expensive as already dealing with the BART Model thus to save computation

classifier/ categorizer:
used vertorization
to check the cosine similarity= confidence
based on the cnfidence the blog is categorized