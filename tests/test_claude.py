from unittest.mock import MagicMock, patch
from src.services.rag_service import RAGAnswerService
from src.agents.judge import DiagnosisJudgeAgent
import src.utils.config as config
from fastapi.testclient import TestClient
from src.main import app


def test_claude_config_aliases():
    assert hasattr(config, 'ANTHROPIC_API_KEY')
    assert hasattr(config, 'CLAUDE_API_KEY')
    assert hasattr(config, 'ANTHROPIC_MODEL')
    assert hasattr(config, 'LLM_PROVIDER')


def test_health_reports_claude_and_provider_fields():
    client = TestClient(app)
    res = client.get('/health')
    assert res.status_code == 200
    data = res.json()
    assert 'claude_configured' in data
    assert 'openai_configured' in data
    assert 'llm_provider' in data


def test_rag_answer_claude_success_flow():
    mock_anthropic_module = MagicMock()
    mock_client = MagicMock()
    mock_anthropic_module.Anthropic.return_value = mock_client
    
    # Mock message response
    mock_content = MagicMock()
    mock_content.text = "Claude evidence-grounded answer: Check cell interference and handover parameters."
    mock_client.messages.create.return_value = MagicMock(content=[mock_content])

    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'sk-ant-test12345', 'LLM_PROVIDER': 'anthropic'}), \
         patch('src.services.rag_service.ANTHROPIC_API_KEY', 'sk-ant-test12345'), \
         patch('src.services.rag_service.LLM_PROVIDER', 'anthropic'), \
         patch.dict('sys.modules', {'anthropic': mock_anthropic_module}):
        
        service = RAGAnswerService()
        assert service.enabled is True
        
        result = service.answer(
            query="High packet loss on cell A",
            diagnosis={'query_analysis': {'corrective_actions': ['Inspect cell A']}, 'similar_incidents': []},
            contexts=["Historical record for cell A"]
        )
        assert result['method'] == 'Claude-RAG'
        assert result['provider'] == 'anthropic'
        assert "Claude evidence-grounded answer" in result['answer']


def test_rag_answer_claude_exception_falls_back_gracefully():
    mock_anthropic_module = MagicMock()
    mock_client = MagicMock()
    mock_anthropic_module.Anthropic.return_value = mock_client
    mock_client.messages.create.side_effect = RuntimeError("API authentication failed")

    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'sk-ant-test12345', 'LLM_PROVIDER': 'anthropic'}), \
         patch('src.services.rag_service.ANTHROPIC_API_KEY', 'sk-ant-test12345'), \
         patch('src.services.rag_service.LLM_PROVIDER', 'anthropic'), \
         patch.dict('sys.modules', {'anthropic': mock_anthropic_module}):
        
        service = RAGAnswerService()
        result = service.answer(
            query="High packet loss on cell A",
            diagnosis={'query_analysis': {'corrective_actions': ['Inspect cell A']}, 'similar_incidents': []},
            contexts=["Historical record for cell A"]
        )
        assert result['method'] == 'deterministic-fallback'
        assert 'Claude error' in result['llm_error']
        assert 'Inspect cell A' in result['answer']


def test_judge_claude_success_flow():
    mock_anthropic_module = MagicMock()
    mock_client = MagicMock()
    mock_anthropic_module.Anthropic.return_value = mock_client

    mock_content = MagicMock()
    mock_content.text = '{"grounding": 0.95, "completeness": 0.9, "actionability": 0.85, "overall": 0.9, "reason": "Accurate grounding"}'
    mock_client.messages.create.return_value = MagicMock(content=[mock_content])

    with patch('src.agents.judge.ANTHROPIC_API_KEY', 'sk-ant-test12345'), \
         patch('src.agents.judge.LLM_PROVIDER', 'anthropic'), \
         patch.dict('sys.modules', {'anthropic': mock_anthropic_module}):
        
        judge = DiagnosisJudgeAgent()
        result = judge.judge(
            query="High packet loss on cell A",
            diagnosis={'classification': {'category': 'throughput_degradation'}}
        )
        assert result['method'] == 'LLM-as-judge'
        assert result['provider'] == 'anthropic'
        assert result['scores']['overall'] == 0.9
