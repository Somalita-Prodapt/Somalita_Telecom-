import json
from src.utils.config import (
    OPENAI_API_KEY, OPENAI_MODEL,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    LLM_PROVIDER, DEMO_MODE
)


class RAGAnswerService:
    """Evidence-grounded RAG synthesis with deterministic corrective-action fallback."""

    def __init__(self):
        self.enabled = (bool(ANTHROPIC_API_KEY) or bool(OPENAI_API_KEY)) and not DEMO_MODE

    def answer(self, query, diagnosis, contexts):
        if self.enabled:
            prompt = {
                'query': query,
                'retrieved_evidence': contexts,
                'diagnosis': diagnosis,
                'query_analysis': diagnosis.get('query_analysis', {}),
                'corrective_actions': diagnosis.get('query_analysis', {}).get(
                    'corrective_actions', diagnosis.get('recommendations', [])
                ),
                'instruction': (
                    'Answer as a telecom NOC decision-support assistant. Use only the supplied '
                    'evidence. Separate observed evidence from hypotheses. If a trend is requested, '
                    'only call it validated when query_analysis.trend_status is validated. If no '
                    'dated evidence exists, explicitly say the trend cannot be confirmed from the '
                    'retrieved records. Provide a concise assessment followed by query-specific '
                    'corrective actions and post-change monitoring checks. Do not invent cell IDs, '
                    'dates, telemetry, root causes or executed changes. Never claim a configuration '
                    'change was executed.'
                )
            }
            system_msg = (
                'You provide evidence-grounded telecom network operations guidance. '
                'Do not invent telemetry or treat candidate causes as confirmed causes.'
            )

            use_anthropic = bool(ANTHROPIC_API_KEY) and (
                LLM_PROVIDER in ('anthropic', 'claude') or
                (LLM_PROVIDER == 'auto' and not OPENAI_API_KEY) or
                (LLM_PROVIDER == 'auto' and ANTHROPIC_API_KEY)
            )
            use_openai = bool(OPENAI_API_KEY) and (
                LLM_PROVIDER == 'openai' or (LLM_PROVIDER == 'auto' and not use_anthropic)
            )

            if use_anthropic:
                try:
                    from anthropic import Anthropic

                    client = Anthropic(api_key=ANTHROPIC_API_KEY)
                    r = client.messages.create(
                        model=ANTHROPIC_MODEL,
                        max_tokens=2048,
                        temperature=0,
                        system=system_msg,
                        messages=[
                            {'role': 'user', 'content': json.dumps(prompt, default=str)}
                        ]
                    )
                    text = ''.join(b.text for b in r.content if getattr(b, 'text', None))
                    return {
                        'answer': text,
                        'method': 'Claude-RAG',
                        'provider': 'anthropic',
                        'model': ANTHROPIC_MODEL,
                        'grounded': True
                    }
                except Exception as e:
                    fallback = self._fallback(query, diagnosis)
                    fallback.update({'method': 'deterministic-fallback', 'llm_error': f'Claude error: {e}'})
                    return fallback

            elif use_openai:
                try:
                    from openai import OpenAI

                    client = OpenAI(api_key=OPENAI_API_KEY)
                    r = client.chat.completions.create(
                        model=OPENAI_MODEL,
                        temperature=0,
                        messages=[
                            {
                                'role': 'system',
                                'content': system_msg
                            },
                            {'role': 'user', 'content': json.dumps(prompt, default=str)}
                        ]
                    )
                    return {
                        'answer': r.choices[0].message.content,
                        'method': 'LLM-RAG',
                        'provider': 'openai',
                        'model': OPENAI_MODEL,
                        'grounded': True
                    }
                except Exception as e:
                    fallback = self._fallback(query, diagnosis)
                    fallback.update({'method': 'deterministic-fallback', 'llm_error': f'OpenAI error: {e}'})
                    return fallback

        return self._fallback(query, diagnosis)

    @staticmethod
    def _number(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _fallback(self, query, d):
        incidents = d.get('similar_incidents', [])
        qa = d.get('query_analysis', {}) or {}
        root = d.get('root_cause', {}) or {}

        fault_values = [
            self._number(x.get('metadata', {}).get('Fault Occurrence Rate (%)'))
            for x in incidents
        ]
        handover_values = [
            self._number(x.get('metadata', {}).get('Handover Success Rate (%)'), 100.0)
            for x in incidents
        ]

        unique_cells = {
            str(x.get('metadata', {}).get('Cell ID') or
                x.get('metadata', {}).get('cell_id') or
                x.get('metadata', {}).get('City') or
                'unknown')
            for x in incidents
        }
        unique_cells.discard('unknown')

        lines = [
            'Evidence-grounded assessment:',
            f"Retrieved {len(incidents)} historical observation(s)"
            + (f" across {len(unique_cells)} cell/site group(s)." if unique_cells else ".")
        ]

        if fault_values:
            lines.append(
                f"Fault occurrence ranges from {min(fault_values):.2f}% to {max(fault_values):.2f}%."
            )
        if handover_values:
            lines.append(
                f"Handover success ranges from {min(handover_values):.2f}% to {max(handover_values):.2f}%."
            )

        if qa.get('trend_requested'):
            status = qa.get('trend_status')
            if status == 'validated':
                lines.append(f"Trend validation: {qa.get('evidence_note')}")
            else:
                lines.append(f"Trend validation: {qa.get('evidence_note')}")

        cause = root.get('primary_cause')
        if cause:
            lines.append(
                "Agent-indicated contributing condition: "
                f"{str(cause).replace('_', ' ')}. This is a hypothesis, not a confirmed root cause."
            )

        recs = qa.get('corrective_actions') or d.get('recommendations', [])
        if recs:
            lines.append('')
            lines.append('Recommended corrective actions:')
            for i, rec in enumerate(recs[:6], 1):
                lines.append(f'{i}. {rec}')

        lines.append('')
        lines.append(
            'These are candidate decision-support actions, not confirmed root causes or automatic '
            'network changes. Validate against live telemetry and approved NOC/change-management procedures.'
        )

        return {
            'answer': '\n'.join(lines),
            'method': 'deterministic-RAG-fallback',
            'grounded': True
        }
