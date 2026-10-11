"""Run deterministic retrieval evaluation from the repository root or this script path."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.rag.retriever import HybridRetriever
from src.services.evaluation import retrieval_test, write_report

with (ROOT / 'evaluation/test_cases.json').open(encoding='utf-8') as handle:
    cases = json.load(handle)
retriever = HybridRetriever()
result = retrieval_test(retriever, cases)
result['dataset_rows_loaded'] = int(len(retriever.df))
result['dataset_scope_note'] = ('Full configured dataset' if len(retriever.df) >= 100000 else 'Sample/fallback dataset; rerun with the official 100K CSV present for full-dataset evaluation')
write_report(result, str(ROOT / 'docs/Evaluation_Report.md'))
print(json.dumps(result, indent=2))
