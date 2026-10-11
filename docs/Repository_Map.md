# Repository Map

```text
Telecom_NetOps_AI_Assistant_Updated/
├── architecture/                 # Architecture diagram + explanation
├── design/                       # Design document
├── src/
│   ├── api/                      # API package placeholder/extension point
│   ├── agents/                   # Classifier, priority, risk, performance, RCA, impact, recommendation, judge, orchestration
│   ├── rag/                      # Preprocessing + hybrid retrieval
│   ├── services/                 # RAG answer, feedback, evaluation
│   ├── utils/                    # Config, models, guardrails
│   └── main.py                   # FastAPI entry point
├── data/sample_data/             # Offline demo fixture
├── docs/                         # API, dataset, evaluation, submission documents
├── evaluation/                   # Test cases + DeepEval/RAGAS hooks
├── tests/                        # Automated tests
├── presentation/                 # Panel deck
├── scripts/                      # Dataset download + index build
├── models/                       # Local trained model artifacts (generated)
├── storage/                      # Chroma + SQLite artifacts (generated)
├── reference/                    # Official project/submission PDFs
├── frontend.py                   # Streamlit command center
├── requirements.txt
├── .env.example
└── README.md
```

- `src/agents/query_analysis.py` — query-specific trend validation and corrective-action analysis.
