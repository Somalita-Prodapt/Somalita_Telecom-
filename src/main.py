from fastapi import FastAPI, HTTPException, Response
from src.rag.retriever import HybridRetriever
from src.rag.preprocessing import load_dataset
from src.utils.config import (
    DATASET_PATH, SAMPLE_DATASET_PATH, USE_SENTENCE_TRANSFORMERS, DEMO_MODE,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL, OPENAI_API_KEY, OPENAI_MODEL, LLM_PROVIDER
)
from src.agents.orchestrator import NetOpsOrchestrator
from src.services.feedback import FeedbackService
from src.services.evaluation import retrieval_test, get_ragas_evaluation, get_deepeval_evaluation
from src.utils.guardrails import validate_query
from src.utils.models import SearchRequest, DiagnosisRequest, FeedbackRequest
import json
import logging
import time
import pandas as pd

logger = logging.getLogger('netops.api')

app=FastAPI(title='AI-Powered Telecom Network Operations Assistant',version='3.0.0',description='Evidence-grounded 5G NetOps RAG and multi-agent decision-support API')
_retriever=None; _orch=None; _feedback=FeedbackService()

def services():
    global _retriever,_orch
    if _retriever is None:
        _retriever=HybridRetriever(); _orch=NetOpsOrchestrator(_retriever)
    return _retriever,_orch

@app.get('/health')
def health():
    # Keep the probe lightweight, but report the actual bundled/official dataset size.
    try:
        df = load_dataset(DATASET_PATH if DATASET_PATH.exists() else SAMPLE_DATASET_PATH)
        incident_count = len(df)
    except Exception:
        incident_count = 0

    if DEMO_MODE:
        active_provider = 'offline-demo (deterministic)'
    elif ANTHROPIC_API_KEY and (LLM_PROVIDER in ('anthropic', 'claude', 'auto')):
        active_provider = f'anthropic ({ANTHROPIC_MODEL})'
    elif OPENAI_API_KEY and (LLM_PROVIDER in ('openai', 'auto')):
        active_provider = f'openai ({OPENAI_MODEL})'
    else:
        active_provider = 'deterministic-fallback (no live LLM key)'

    return {
        'status':'ok',
        'service':app.title,
        'version':app.version,
        'incident_count':incident_count,
        'semantic_embeddings_configured':bool(USE_SENTENCE_TRANSFORMERS),
        'demo_mode': DEMO_MODE,
        'claude_configured': bool(ANTHROPIC_API_KEY),
        'openai_configured': bool(OPENAI_API_KEY),
        'llm_provider': active_provider,
        'semantic_retrieval_status':'initializes on first search; TF-IDF semantic fallback is available',
        'message':'API process is healthy'
    }

@app.get('/metadata')
def metadata():
    r,_=services(); df=r.df
    return {'incident_count':len(df),'states':sorted(df.State.dropna().astype(str).unique().tolist()),'cities':sorted(df.City.dropna().astype(str).unique().tolist()),'seasons':sorted(df.Season.dropna().astype(str).unique().tolist()),'weather':sorted(df.Weather.dropna().astype(str).unique().tolist()),'network_conditions':['Healthy','At Risk','Degraded']}

@app.get('/stats')
def stats():
    r,_=services(); df=r.df
    condition_counts=df.apply(r.network_condition,axis=1).value_counts().to_dict()
    season_counts=df['Season'].astype(str).value_counts().to_dict()
    return {'incident_count':len(df),'avg_latency_ms':round(float(df['Latency (ms)'].mean()),2),'avg_throughput_mbps':round(float(df['Throughput (Mbps)'].mean()),2),'avg_packet_loss_pct':round(float(df['Packet Loss Rate (%)'].mean()),2),'avg_fault_occurrence_pct':round(float(df['Fault Occurrence Rate (%)'].mean()),2),'high_risk_rows':int((df['Fault Occurrence Rate (%)']>=50).sum()),'network_condition_counts':condition_counts,'season_counts':season_counts}

@app.post('/search-incidents')
def search(req:SearchRequest, page:int=1, page_size:int=500):
    try:
        started=time.perf_counter()
        q=validate_query(req.query); r,_=services()
        page=max(1,int(page)); page_size=min(max(1,int(page_size)),1000)
        filters=req.model_dump(exclude={'query','top_k'})
        offset=(page-1)*page_size
        exact=r.search(q,req.top_k,req.state,req.city,req.season,req.weather,req.network_condition,offset=offset,page_size=page_size)
        diagnostics=r.filter_diagnostics(**filters)
        total=int(diagnostics.get('exact_match_count',0))
        relaxed=[]; mode='exact'; results=exact
        if not results and offset==0:
            results,relaxed=r.nearest_filter_matches(q,req.top_k,**filters)
            total=int(diagnostics.get('exact_match_count',0))
            mode='near_match' if results else 'no_match'
        logger.info('incident_search query_chars=%d matched=%d returned=%d mode=%s elapsed_ms=%.2f', len(q), int(total), len(results), mode, (time.perf_counter()-started)*1000)
        return {'query':q,'filters':filters,'results':results,'match_mode':mode,'relaxed_filters':relaxed,'filter_diagnostics':diagnostics,
                'total_results':int(total),'page':page,'page_size':page_size,'retrieval_scope':'entire filtered dataset','display_limit':req.top_k}
    except Exception as e: raise HTTPException(400,str(e))


@app.get('/incidents/{incident_id}')
def incident(incident_id:str):
    r,_=services(); hit=r.df[r.df.incident_id.astype(str)==incident_id]
    if hit.empty: raise HTTPException(404,'Incident not found')
    row=hit.iloc[0]
    return {'incident_id':incident_id,'metadata':row.to_dict()}

@app.post('/diagnose')
def diagnose(req:DiagnosisRequest):
    try:
        started=time.perf_counter()
        q=validate_query(req.query); _,o=services(); result=o.diagnose({**req.model_dump(),'query':q})
        logger.info('diagnosis query_chars=%d matched=%d returned=%d elapsed_ms=%.2f', len(q), result.get('whole_dataset_match_count',0), len(result.get('similar_incidents',[])), (time.perf_counter()-started)*1000)
        return result
    except Exception as e: raise HTTPException(400,str(e))

@app.post('/feedback')
def feedback(req:FeedbackRequest): return _feedback.add(req.query,req.incident_id,req.rating,req.comment)
@app.get('/feedback/summary')
def feedback_summary(): return _feedback.summary()
@app.get('/feedback/recent')
def feedback_recent(limit:int=50): return _feedback.recent(min(max(limit,1),200))



def _dataset_enrichment(df):
    """Create display-only fields for Dataset Explorer without modifying the source data."""
    out = df.copy()

    def num_series(column, default=0.0):
        if column in out.columns:
            return pd.to_numeric(out[column], errors='coerce').fillna(default)
        return pd.Series(default, index=out.index, dtype=float)

    availability = num_series('Cell Availability (%)')
    fault = num_series('Fault Occurrence Rate (%)')
    risk = (0.70 * fault + 0.30 * (100.0 - availability)).clip(0, 100)
    if 'Risk Index' not in out.columns:
        out['Risk Index'] = risk.round(1)

    if 'Circle' not in out.columns:
        out['Circle'] = out['City'].astype(str) if 'City' in out.columns else 'Unknown'

    if 'Severity' not in out.columns:
        out['Severity'] = pd.cut(
            out['Risk Index'],
            bins=[-float('inf'), 25, 35, 45, float('inf')],
            labels=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
            right=False
        ).astype(str)

    if 'Issue Type' not in out.columns:
        call_drop = num_series('Call Drop Rate (%)')
        handover = num_series('Handover Success Rate (%)', 100)
        packet_loss = num_series('Packet Loss Rate (%)')
        signal = num_series('Signal Strength (dBm)', 0)
        latency = num_series('Latency (ms)')
        throughput = num_series('Throughput (Mbps)', 0)
        issue = pd.Series('Other', index=out.index, dtype='object')
        issue.loc[call_drop >= 3] = 'Dropped Calls'
        issue.loc[(call_drop < 3) & (handover < 95)] = 'Handover Failures'
        issue.loc[(call_drop < 3) & (handover >= 95) & (packet_loss >= 6)] = 'Packet Loss'
        issue.loc[(call_drop < 3) & (handover >= 95) & (packet_loss < 6) & (signal <= -105)] = 'Coverage Gap'
        issue.loc[(call_drop < 3) & (handover >= 95) & (packet_loss < 6) & (signal > -105) & (latency >= 100)] = 'Backhaul'
        issue.loc[(call_drop < 3) & (handover >= 95) & (packet_loss < 6) & (signal > -105) & (latency < 100) & (throughput < 300)] = 'Backhaul'
        issue.loc[(issue == 'Other') & ((packet_loss >= 8) | (num_series('Jitter (ms)') >= 30))] = 'Interference'
        out['Issue Type'] = issue

    return out




@app.post('/search-incidents/export')
def search_export(req:SearchRequest):
    try:
        q=validate_query(req.query); r,_=services()
        df=r.search_export_dataframe(q,req.state,req.city,req.season,req.weather,req.network_condition)
        return Response(content=df.to_csv(index=False), media_type='text/csv', headers={'Content-Disposition':'attachment; filename=netops_search_evidence.csv'})
    except Exception as e: raise HTTPException(400,str(e))


@app.get('/dataset/options')
def dataset_options():
    """Return filter choices for Dataset Explorer from the full loaded dataset."""
    r, _ = services()
    df = _dataset_enrichment(r.df)
    return {
        'circle': sorted(df['Circle'].dropna().astype(str).unique().tolist()),
        'severity': sorted(df['Severity'].dropna().astype(str).unique().tolist()),
        'season': sorted(df['Season'].dropna().astype(str).unique().tolist()) if 'Season' in df.columns else [],
        'issue_type': sorted(df['Issue Type'].dropna().astype(str).unique().tolist()),
        'total_count': int(len(df)),
    }


@app.get('/dataset')
def dataset(
    circle: str | None = None,
    severity: str | None = None,
    season: str | None = None,
    issue_type: str | None = None,
    sort_by: str = 'Highest Risk',
    page: int = 1,
    page_size: int = 500
):
    """Return the complete filtered dataset for the Dataset Explorer.

    Filtering is applied server-side to a copy of the loaded dataframe. The source
    dataset and existing retrieval/diagnosis behavior are not modified, and no top-k
    limit is applied to this explorer.
    """
    r, _ = services()
    df = _dataset_enrichment(r.df)

    def clean(value):
        if value is None:
            return None
        value = str(value).strip()
        return None if not value or value.lower() == 'all' else value.casefold()

    selections = {
        'Circle': clean(circle),
        'Severity': clean(severity),
        'Season': clean(season),
        'Issue Type': clean(issue_type),
    }

    for column, value in selections.items():
        if value is not None and column in df.columns:
            df = df[df[column].astype(str).str.strip().str.casefold().eq(value)]

    sort_map = {
        'Highest Risk': ('Risk Index', False),
        'Lowest Risk': ('Risk Index', True),
        'Latest Date': (next((c for c in df.columns if str(c).casefold() in {'date', 'timestamp', 'observation_date', 'observation date'}), None), False),
        'Oldest Date': (next((c for c in df.columns if str(c).casefold() in {'date', 'timestamp', 'observation_date', 'observation date'}), None), True),
        'Highest Fault Occurrence': ('Fault Occurrence Rate (%)', False),
        'Lowest Handover Success': ('Handover Success Rate (%)', True),
        'Highest Latency': ('Latency (ms)', False),
        'Highest Throughput': ('Throughput (Mbps)', False),
    }
    sort_col, ascending = sort_map.get(sort_by, ('Risk Index', False))
    if sort_col and sort_col in df.columns:
        if 'Date' in sort_by or 'date' in str(sort_col).lower():
            sortable = pd.to_datetime(df[sort_col], errors='coerce')
            df = df.assign(_dataset_sort=sortable).sort_values('_dataset_sort', ascending=ascending, na_position='last').drop(columns=['_dataset_sort'])
        else:
            df = df.sort_values(sort_col, ascending=ascending, na_position='last')

    # Preserve every original dataset column plus the explorer's display-only fields.
    # Filtering and sorting above operate on the complete loaded dataset; only one
    # display page is serialized so the browser is never forced to receive 100K rows.
    page=max(1,int(page)); page_size=min(max(1,int(page_size)),1000)
    start=(page-1)*page_size
    page_df=df.iloc[start:start+page_size]
    records=json.loads(page_df.to_json(orient='records', date_format='iso'))
    return {
        'total_count': int(len(r.df)),
        'filtered_count': int(len(df)),
        'columns': list(df.columns),
        'rows': records,
        'filters': {k: v for k, v in selections.items() if v is not None},
        'sort_by': sort_by,
        'page': page,
        'page_size': page_size,
        'page_count': int((len(df)+page_size-1)//page_size),
        'retrieval_scope': 'entire loaded dataset',
    }

@app.get('/dataset/export')
def dataset_export(circle: str | None=None, severity: str | None=None, season: str | None=None,
                   issue_type: str | None=None, sort_by: str='Highest Risk'):
    r,_=services(); df=_dataset_enrichment(r.df)
    def clean(value):
        if value is None: return None
        value=str(value).strip()
        return None if not value or value.lower()=='all' else value.casefold()
    selections={'Circle':clean(circle),'Severity':clean(severity),'Season':clean(season),'Issue Type':clean(issue_type)}
    for column,value in selections.items():
        if value is not None and column in df.columns:
            df=df[df[column].astype(str).str.strip().str.casefold().eq(value)]
    sort_map={'Highest Risk':('Risk Index',False),'Lowest Risk':('Risk Index',True),
              'Highest Fault Occurrence':('Fault Occurrence Rate (%)',False),
              'Lowest Handover Success':('Handover Success Rate (%)',True),
              'Highest Latency':('Latency (ms)',False),'Highest Throughput':('Throughput (Mbps)',False)}
    sort_col,ascending=sort_map.get(sort_by,(None,False))
    if sort_col and sort_col in df.columns: df=df.sort_values(sort_col,ascending=ascending,na_position='last')
    return Response(content=df.to_csv(index=False), media_type='text/csv', headers={'Content-Disposition':'attachment; filename=telecom_dataset_filtered.csv'})


@app.post('/evaluate/retrieval')
def evaluate_retrieval():
    r,_=services(); cases=json.load(open('evaluation/test_cases.json',encoding='utf-8')); return retrieval_test(r,cases)


@app.post('/evaluate/ragas')
@app.get('/evaluate/ragas')
def evaluate_ragas(run_live: bool = False):
    r, _ = services()
    return get_ragas_evaluation(r, run_live=run_live)


@app.post('/evaluate/deepeval')
@app.get('/evaluate/deepeval')
def evaluate_deepeval(run_live: bool = False):
    r, _ = services()
    return get_deepeval_evaluation(r, run_live=run_live)

