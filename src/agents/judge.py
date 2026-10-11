import json
from src.utils.config import (
    OPENAI_API_KEY, OPENAI_MODEL,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    LLM_PROVIDER, DEMO_MODE
)


class DiagnosisJudgeAgent:
    def judge(self, query, diagnosis):
        has_anthropic = bool(ANTHROPIC_API_KEY)
        has_openai = bool(OPENAI_API_KEY)
        if (has_anthropic or has_openai) and not DEMO_MODE:
            compact = {
                k: diagnosis.get(k)
                for k in [
                    'classification', 'prioritization', 'risk_prediction',
                    'performance_prediction', 'root_cause', 'network_impact',
                    'recommendations', 'query_analysis', 'rag_answer',
                    'filter_diagnostics'
                ]
            }
            compact['whole_dataset_match_count'] = len(diagnosis.get('similar_incidents', []))
            system_prompt = (
                'You are a telecom NOC evaluator. Return JSON only with numeric grounding, '
                'completeness, actionability and overall scores from 0 to 1, plus one short reason. '
                'Evaluate whole-dataset evidence counts and aggregate evidence; do not require a top-k sample.'
            )
            user_content = f"Query: {query}\nDiagnosis summary: {json.dumps(compact, default=str)}"

            use_anthropic = has_anthropic and (
                LLM_PROVIDER in ('anthropic', 'claude') or
                (LLM_PROVIDER == 'auto' and not has_openai) or
                (LLM_PROVIDER == 'auto' and has_anthropic)
            )
            use_openai = has_openai and (
                LLM_PROVIDER == 'openai' or (LLM_PROVIDER == 'auto' and not use_anthropic)
            )

            if use_anthropic:
                try:
                    from anthropic import Anthropic

                    client = Anthropic(api_key=ANTHROPIC_API_KEY)
                    r = client.messages.create(
                        model=ANTHROPIC_MODEL,
                        max_tokens=600,
                        temperature=0,
                        system=system_prompt,
                        messages=[{'role': 'user', 'content': user_content}]
                    )
                    raw = ''.join(b.text for b in r.content if getattr(b, 'text', None)) or '{}'
                    try:
                        return {'method': 'LLM-as-judge', 'scores': json.loads(raw), 'provider': 'anthropic', 'model': ANTHROPIC_MODEL}
                    except Exception:
                        return {'method': 'LLM-as-judge', 'raw': raw, 'provider': 'anthropic', 'model': ANTHROPIC_MODEL}
                except Exception as e:
                    return {'method': 'fallback', 'overall': 0.75, 'reason': f'Claude judge unavailable: {e}'}

            elif use_openai:
                try:
                    from openai import OpenAI

                    client = OpenAI(api_key=OPENAI_API_KEY)
                    r = client.chat.completions.create(
                        model=OPENAI_MODEL,
                        temperature=0,
                        messages=[
                            {'role': 'system', 'content': system_prompt},
                            {'role': 'user', 'content': user_content}
                        ]
                    )
                    raw = r.choices[0].message.content or '{}'
                    try:
                        return {'method': 'LLM-as-judge', 'scores': json.loads(raw), 'provider': 'openai', 'model': OPENAI_MODEL}
                    except Exception:
                        return {'method': 'LLM-as-judge', 'raw': raw, 'provider': 'openai', 'model': OPENAI_MODEL}
                except Exception as e:
                    return {'method': 'fallback', 'overall': 0.75, 'reason': f'LLM judge unavailable: {e}'}

        fields = [
            'classification', 'risk_prediction', 'performance_prediction',
            'root_cause', 'network_impact', 'recommendations',
            'similar_incidents', 'rag_answer'
        ]
        score = sum(bool(diagnosis.get(f)) for f in fields) / len(fields)
        return {'method': 'deterministic LLM-as-judge-compatible rubric', 'overall': round(score, 3), 'criteria': fields}
