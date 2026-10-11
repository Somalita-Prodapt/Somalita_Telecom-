import re
import pandas as pd


class QueryAnalysisAgent:
    """Adds query-specific, evidence-grounded interpretation without inventing telemetry."""

    TREND_TERMS = (
        'increasing', 'declining', 'decreasing', 'rising', 'falling',
        'trend', 'over time', 'worsening'
    )
    DATE_COLUMNS = (
        'observation_date', 'observation date', 'date', 'timestamp',
        'datetime', 'Date', 'Timestamp', 'Observation Date'
    )
    GROUP_COLUMNS = (
        'cell_id', 'Cell ID', 'cell_id', 'Cell_ID',
        'site_id', 'Site ID', 'City', 'city', 'Region', 'region'
    )

    def _find_column(self, rows, candidates):
        if not rows:
            return None
        keys = set()
        for row in rows:
            keys.update(row.keys())
        lower = {str(k).casefold(): k for k in keys}
        for candidate in candidates:
            if candidate in keys:
                return candidate
            hit = lower.get(str(candidate).casefold())
            if hit is not None:
                return hit
        return None

    def _trend_evidence(self, rows):
        """Validate a requested direction only when dated, same-group observations exist."""
        date_col = self._find_column(rows, self.DATE_COLUMNS)
        if not date_col:
            return {
                'status': 'not_validated_time_series',
                'evidence': [],
                'note': (
                    'The retrieved records do not contain a usable timestamp/date field. '
                    'Increasing or declining behavior cannot be confirmed as a time trend '
                    'from these records alone.'
                )
            }

        group_col = self._find_column(rows, self.GROUP_COLUMNS)
        groups = {}
        for row in rows:
            raw_date = row.get(date_col)
            dt = pd.to_datetime(raw_date, errors='coerce')
            if pd.isna(dt):
                continue
            group = str(row.get(group_col, 'all') if group_col else 'all')
            groups.setdefault(group, []).append((dt, row))

        findings = []
        for group, observations in groups.items():
            if len(observations) < 2:
                continue
            observations.sort(key=lambda x: x[0])
            first_date, first = observations[0]
            last_date, last = observations[-1]
            try:
                fault_first = float(first.get('Fault Occurrence Rate (%)'))
                fault_last = float(last.get('Fault Occurrence Rate (%)'))
                ho_first = float(first.get('Handover Success Rate (%)'))
                ho_last = float(last.get('Handover Success Rate (%)'))
            except (TypeError, ValueError):
                continue

            fault_delta = fault_last - fault_first
            ho_delta = ho_last - ho_first
            findings.append({
                'group': group,
                'start_date': str(first_date.date()),
                'end_date': str(last_date.date()),
                'fault_start_pct': round(fault_first, 2),
                'fault_end_pct': round(fault_last, 2),
                'fault_delta_pp': round(fault_delta, 2),
                'handover_start_pct': round(ho_first, 2),
                'handover_end_pct': round(ho_last, 2),
                'handover_delta_pp': round(ho_delta, 2),
                'validated': fault_delta > 0 and ho_delta < 0,
            })

        validated = [x for x in findings if x['validated']]
        if validated:
            note_parts = []
            for x in validated[:3]:
                label = f"{group_col or 'group'} {x['group']}"
                note_parts.append(
                    f"{label}: fault occurrence {x['fault_start_pct']:.2f}% → "
                    f"{x['fault_end_pct']:.2f}% ({x['fault_delta_pp']:+.2f} pp), "
                    f"handover success {x['handover_start_pct']:.2f}% → "
                    f"{x['handover_end_pct']:.2f}% ({x['handover_delta_pp']:+.2f} pp), "
                    f"{x['start_date']} → {x['end_date']}"
                )
            return {
                'status': 'validated',
                'evidence': validated[:3],
                'note': (
                    'The requested direction is supported by dated same-group evidence: '
                    + '; '.join(note_parts)
                    + '. Continue validating against production telemetry.'
                )
            }

        if findings:
            return {
                'status': 'mixed_or_not_supported',
                'evidence': findings[:3],
                'note': (
                    'Dated same-group observations are available, but the retrieved '
                    'observations do not consistently support increasing fault occurrence '
                    'together with declining handover success.'
                )
            }

        return {
            'status': 'insufficient_time_series',
            'evidence': [],
            'note': (
                'A date field is present, but the retrieved evidence does not contain '
                'enough same-group dated observations to validate the requested trend.'
            )
        }

    def analyze(self, query, incidents):
        q = (query or '').lower()
        wants_trend = any(t in q for t in self.TREND_TERMS)
        rows = [x.get('metadata', {}) for x in incidents] if incidents else []

        metrics = {}
        if rows:
            fault = pd.to_numeric(
                pd.Series([r.get('Fault Occurrence Rate (%)') for r in rows]),
                errors='coerce'
            )
            handover = pd.to_numeric(
                pd.Series([r.get('Handover Success Rate (%)') for r in rows]),
                errors='coerce'
            )
            metrics = {
                'retrieved_fault_occurrence_min_pct': round(float(fault.min()), 2),
                'retrieved_fault_occurrence_max_pct': round(float(fault.max()), 2),
                'retrieved_handover_success_min_pct': round(float(handover.min()), 2),
                'retrieved_handover_success_max_pct': round(float(handover.max()), 2),
            }

        trend = self._trend_evidence(rows) if wants_trend else {
            'status': 'not_requested',
            'evidence': [],
            'note': 'A time trend was not explicitly requested.'
        }

        actions = []

        if any(term in q for term in ('handover', 'handoff', 'mobility')):
            actions.extend([
                'Investigate handover failures by source/target cell pair, mobility pattern and failure cause; review neighbor-cell relations and handover thresholds.',
                'Check radio coverage, signal quality and interference in affected cells, including coverage holes and weak serving/target-cell conditions.',
                'Review recent handover/radio parameter changes, failed configuration changes and correlated alarm patterns before proposing changes.'
            ])

        if any(term in q for term in ('fault', 'failure', 'outage')):
            actions.append(
                'Prioritize cells with high fault occurrence and correlate faults with availability, packet loss, call drops, alarms and MTTR to isolate the operational driver.'
            )

        if any(term in q for term in ('packet loss', 'packet-loss')):
            actions.append(
                'Check radio/transport link quality, retransmissions, packet-error counters and congestion indicators; correlate packet loss with latency and throughput.'
            )

        if any(term in q for term in ('latency', 'throughput', 'congestion', 'capacity')):
            actions.append(
                'Review utilization, transport latency and traffic distribution; compare affected cells with healthy peers before considering load balancing or capacity changes.'
            )

        if wants_trend:
            actions.append(
                'Validate the trend with dated observations from the same cell/region; compare first-vs-last periods and calculate the change before treating the direction as confirmed.'
            )

        actions.append(
            'After approved corrective action, monitor handover success, fault occurrence, call drops, availability, packet loss and relevant alarms against a pre-change baseline.'
        )

        actions = list(dict.fromkeys(actions))

        return {
            'trend_requested': wants_trend,
            'trend_status': trend['status'],
            'trend_validation': trend['evidence'],
            'evidence_note': trend['note'],
            'retrieved_metric_range': metrics,
            'corrective_actions': actions[:6],
        }
