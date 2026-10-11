"""Run RAGAS evaluation on the project's real retrieval pipeline.

Requires: pip install -r requirements.txt and a supported LLM configuration.
Set OPENAI_API_KEY in .env for the default OpenAI-backed RAGAS evaluator.
"""
import os
from pathlib import Path
from src.rag.retriever import HybridRetriever

def main():
    try:
        from ragas import EvaluationDataset, SingleTurnSample, evaluate
        from ragas.metrics import Faithfulness, ResponseRelevancy, LLMContextPrecisionWithoutReference
        from ragas.llms import LangchainLLMWrapper
        from langchain_openai import ChatOpenAI
    except Exception as exc:
        raise SystemExit('RAGAS dependencies are not available. Install requirements.txt and ensure langchain-openai is installed: '+str(exc))
    if not os.getenv('OPENAI_API_KEY'):
        raise SystemExit('Set OPENAI_API_KEY in .env before running RAGAS evaluation.')
    retriever=HybridRetriever()
    cases=[
        ('High latency, packet loss and reduced throughput', 'Find similar historical network incidents and explain likely causes.'),
        ('Increasing alarms and poor handover success', 'Retrieve evidence for this network degradation pattern.'),
    ]
    samples=[]
    for query,answer in cases:
        docs=retriever.search(query,top_k=5)
        samples.append(SingleTurnSample(user_input=query,response=answer,retrieved_contexts=[x['document'] for x in docs]))
    dataset=EvaluationDataset(samples=samples)
    llm=LangchainLLMWrapper(ChatOpenAI(model=os.getenv('OPENAI_MODEL','gpt-4o-mini'),temperature=0))
    metrics=[Faithfulness(llm=llm),ResponseRelevancy(llm=llm),LLMContextPrecisionWithoutReference(llm=llm)]
    result=evaluate(dataset,metrics=metrics)
    print(result)
    out=Path('docs/ragas_results.json'); out.write_text(result.to_pandas().to_json(orient='records',indent=2),encoding='utf-8')
    print(f'Wrote {out}')

if __name__=='__main__': main()
