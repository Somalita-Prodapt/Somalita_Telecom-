from pathlib import Path
import os
import logging
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / '.env')
DATASET_PATH = ROOT / os.getenv('DATASET_PATH', 'data/raw/5G_netops_data_100K.csv')
SAMPLE_DATASET_PATH = ROOT / 'data/sample_data/netops_sample.csv'
# The application always prefers the configured/full dataset. If that path is absent,
# preprocessing.py discovers the first CSV in data/raw before falling back to the 5-row fixture.
DATASET_SEARCH_DIR = ROOT / 'data/raw'
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
# For the 100K dataset, TF-IDF lexical/semantic retrieval is the fast deterministic default.
# Sentence-transformer embeddings remain supported when explicitly enabled for smaller datasets.
USE_SENTENCE_TRANSFORMERS = os.getenv('USE_SENTENCE_TRANSFORMERS', 'false').lower() == 'true'
VECTOR_DB_PATH = ROOT / os.getenv('VECTOR_DB_PATH', 'storage/chroma')
MODEL_PATH = ROOT / os.getenv('MODEL_PATH', 'models')
STORAGE_PATH = ROOT / os.getenv('STORAGE_PATH', 'storage')
# Legacy top-k environment setting intentionally removed from application defaults.
SEMANTIC_WEIGHT = float(os.getenv('SEMANTIC_WEIGHT', '0.65'))
LEXICAL_WEIGHT = float(os.getenv('LEXICAL_WEIGHT', '0.35'))
SEMANTIC_CANDIDATES = int(os.getenv('SEMANTIC_CANDIDATES', '40'))
LEXICAL_CANDIDATES = int(os.getenv('LEXICAL_CANDIDATES', '40'))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY') or os.getenv('CLAUDE_API_KEY') or ''
CLAUDE_API_KEY = ANTHROPIC_API_KEY
ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL') or os.getenv('CLAUDE_MODEL') or 'claude-3-5-sonnet-20241022'
CLAUDE_MODEL = ANTHROPIC_MODEL
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'auto').lower()
ALLOW_SAMPLE_FALLBACK = os.getenv('ALLOW_SAMPLE_FALLBACK', 'true').lower() == 'true'

DEMO_MODE = os.getenv('DEMO_MODE', 'false').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO), format='%(asctime)s %(levelname)s %(name)s %(message)s')
