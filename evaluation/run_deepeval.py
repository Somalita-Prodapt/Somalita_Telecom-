"""DeepEval evaluation hook. Configure OPENAI_API_KEY if using an LLM-backed DeepEval judge."""
from src.rag.retriever import HybridRetriever
try:
    from deepeval import evaluate
    from deepeval.test_case import LLMTestCase
    from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
except Exception as e:
    raise SystemExit(f"Install/configure DeepEval first: {e}")
r=HybridRetriever(); q='high latency packet loss reduced throughput'; docs=r.search(q,top_k=5); context=[x['document'] for x in docs]
answer='Retrieved historical incidents and network evidence for the requested condition.'
test=LLMTestCase(input=q,actual_output=answer,retrieval_context=context)
evaluate([test],[AnswerRelevancyMetric(threshold=0.5),FaithfulnessMetric(threshold=0.5)])
