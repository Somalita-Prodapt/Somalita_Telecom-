from .classifier import IncidentClassifierAgent
from .prioritizer import IncidentPrioritizerAgent
from .risk import FaultRiskAgent
from .performance import PerformancePredictionAgent
from .root_cause import RootCauseAgent, NetworkImpactAgent
from .recommender import TroubleshootingRecommendationAgent
from .judge import DiagnosisJudgeAgent
from .query_analysis import QueryAnalysisAgent
from src.services.rag_service import RAGAnswerService


class NetOpsOrchestrator:
    def __init__(self, retriever):
        self.r = retriever
        self.classifier = IncidentClassifierAgent()
        self.prioritizer = IncidentPrioritizerAgent()
        self.risk = FaultRiskAgent(retriever.df)
        self.performance = PerformancePredictionAgent(retriever.df)
        self.rc = RootCauseAgent()
        self.impact = NetworkImpactAgent()
        self.rec = TroubleshootingRecommendationAgent()
        self.judge = DiagnosisJudgeAgent()
        self.query_analysis = QueryAnalysisAgent()
        self.rag = RAGAnswerService()

    @staticmethod
    def _evidence_summary(df):
        import pandas as pd
        if df is None or df.empty:
            return 'No matching historical records.'
        numeric=['Fault Occurrence Rate (%)','Handover Success Rate (%)','Packet Loss Rate (%)','Latency (ms)','Throughput (Mbps)','Cell Availability (%)','Call Drop Rate (%)']
        lines=[f'Whole-dataset evidence: {len(df):,} matching historical observation(s).']
        for c in numeric:
            if c in df.columns:
                vals=pd.to_numeric(df[c],errors='coerce').dropna()
                if not vals.empty:
                    lines.append(f'{c}: min={vals.min():.2f}, mean={vals.mean():.2f}, max={vals.max():.2f}.')
        for c in ['Season','State','City']:
            if c in df.columns:
                lines.append(f'{c} distinct values={df[c].nunique(dropna=True):,}.')
        return ' '.join(lines)

    def diagnose(self, req):
        query = req['query']
        filters = {
            'state': req.get('state'), 'city': req.get('city'),
            'season': req.get('season'), 'weather': req.get('weather'),
            'network_condition': req.get('network_condition')
        }
        cls = self.classifier.classify(query)
        incidents = self.r.search(query, req.get('top_k'), **filters, offset=0, page_size=500)
        full_df = self.r.df.loc[self.r._filter_mask(**filters)].copy()
        relaxed_filters = []
        match_mode = 'exact'

        if not incidents:
            incidents, relaxed_filters = self.r.nearest_filter_matches(
                query, req.get('top_k'), **filters
            )
            match_mode = 'near_match' if incidents else 'no_match'

        diagnostics = self.r.filter_diagnostics(**filters)
        if not incidents:
            return {
                'status': 'no_match',
                'query': query,
                'classification': cls,
                'similar_incidents': [],
                'filter_diagnostics': diagnostics,
                'match_mode': 'no_match',
                'relaxed_filters': [],
                'message': 'No historical incidents match the selected filters. Choose a compatible filter combination or broaden one filter.'
            }

        row = __import__('pandas').Series(incidents[0]['metadata'])
        risk = self.risk.predict(row)
        perf = self.performance.predict(row)
        rc = self.rc.analyze(row, cls)
        impact = self.impact.analyze(row)
        pri = self.prioritizer.prioritize(incidents)
        rec = self.rec.recommend(row, rc, incidents)
        query_analysis = self.query_analysis.analyze(query, incidents)
        # Query-specific actions are appended without replacing the existing recommendation agent.
        rec = list(dict.fromkeys(rec + query_analysis['corrective_actions']))[:6]
        result = {
            'status': 'ok', 'query': query, 'classification': cls,
            'prioritization': pri, 'risk_prediction': risk,
            'performance_prediction': perf, 'root_cause': rc,
            'network_impact': impact, 'recommendations': rec,
            'similar_incidents': incidents, 'filter_diagnostics': diagnostics,
            'total_results': int(diagnostics.get('exact_match_count', len(full_df))),
            'query_analysis': query_analysis,
            'match_mode': match_mode, 'relaxed_filters': relaxed_filters,
        }
        # RAG searches the entire filtered dataset, while the synthesis prompt uses a compact
        # aggregate evidence summary so a 100K-row dataset never gets truncated to an arbitrary
        # top-5 context and never exceeds the model context window.
        result['evidence_summary'] = self._evidence_summary(full_df)
        result['rag_answer'] = self.rag.answer(query, result, [result['evidence_summary']])
        result['whole_dataset_match_count'] = int(len(full_df))
        result['judge'] = self.judge.judge(query, result)
        result['agent_trace'] = [
            'Guardrail validation', 'Incident classification', 'Hybrid retrieval',
            'Incident prioritization', 'Fault-risk prediction', 'Performance prediction',
            'Root-cause analysis', 'Network-impact analysis', 'Troubleshooting recommendation', 'Query-specific trend/action analysis',
            'RAG synthesis', 'LLM-as-judge validation'
        ]
        return result
