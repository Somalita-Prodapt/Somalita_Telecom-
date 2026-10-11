from fastapi.testclient import TestClient
from src.main import app
def test_health():
    r=TestClient(app).get('/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_search_with_state_city():
    payload={'query':'high latency packet loss reduced throughput','top_k':5,'state':'MN','city':'Schneiderville','season':None,'weather':None,'network_condition':None}
    r=TestClient(app).post('/search-incidents',json=payload)
    assert r.status_code==200
    assert r.json()['match_mode']=='exact'
    assert len(r.json()['results'])>=1


def test_search_conflicting_state_city_returns_near_match_not_400():
    payload={'query':'high latency packet loss reduced throughput','top_k':5,'state':'MN','city':'Lake Heidiside','season':None,'weather':None,'network_condition':None}
    r=TestClient(app).post('/search-incidents',json=payload)
    assert r.status_code==200
    assert r.json()['match_mode'] in {'near_match','no_match'}


def test_health_reports_dataset_and_semantic_status():
    r=TestClient(app).get('/health')
    body=r.json()
    assert body['incident_count'] >= 1
    assert 'semantic_embeddings_configured' in body

def test_handover_fault_query_has_corrective_actions_and_trend_guardrail():
    payload={'query':'A network region has increasing fault occurrence and declining handover success. What corrective actions should be considered?','top_k':5}
    r=TestClient(app).post('/diagnose',json=payload)
    assert r.status_code==200
    body=r.json()
    assert body['query_analysis']['trend_requested'] is True
    assert body['query_analysis']['trend_status']=='not_validated_time_series'
    assert len(body['query_analysis']['corrective_actions']) >= 5
    answer=body['rag_answer']['answer'].lower()
    assert 'corrective actions' in answer
    assert 'dated' in answer


def test_ragas_and_deepeval_evaluation_endpoints():
    c = TestClient(app)
    r_ragas = c.post('/evaluate/ragas')
    assert r_ragas.status_code == 200
    assert 'summary' in r_ragas.json()
    assert 'faithfulness' in r_ragas.json()['summary']

    r_deep = c.post('/evaluate/deepeval')
    assert r_deep.status_code == 200
    assert 'summary' in r_deep.json()
    assert 'pass_rate' in r_deep.json()['summary']

