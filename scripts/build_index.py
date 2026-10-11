from src.rag.retriever import HybridRetriever
print('Building/loading the persistent hybrid index...')
r=HybridRetriever(); print(f'Loaded {len(r.df):,} incidents. Semantic index: {bool(r.embedder and r._chroma)}')
