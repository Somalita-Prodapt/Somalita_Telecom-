class TroubleshootingRecommendationAgent:
    def recommend(self,row,cause,similar):
        rec=[]; c=cause['primary_cause']
        mapping={
        'latency_pressure':'Inspect transport/backhaul latency, queueing and overloaded cells; rebalance traffic where appropriate.',
        'packet_loss_or_link_quality':'Check radio/transport link quality, retransmissions, interference indicators and packet-error counters.',
        'capacity_or_congestion':'Review cell utilization and user distribution; consider traffic steering, load balancing or capacity expansion.',
        'weak_radio_signal':'Review coverage, antenna configuration, power settings and physical obstructions/interference.',
        'handover_instability':'Inspect neighbor relations, handover thresholds and mobility configuration; validate recent parameter changes.',
        'critical_alarm_condition':'Correlate critical alarms with configuration changes and affected cells before remediation.',
        'authentication_instability':'Inspect authentication failures, security events and core-network connectivity.',
        'no_single_dominant_cause_detected':'Correlate the retrieved historical incidents with current telemetry before making a configuration change.'}
        rec.append(mapping.get(c,mapping['no_single_dominant_cause_detected']))
        if float(row['Alarm Count'])>10: rec.append('Prioritize alarm correlation and isolate recurring alarm patterns.')
        if float(row['Fault Occurrence Rate (%)'])>50: rec.append('Escalate for focused fault investigation and monitor the cell after corrective action.')
        if similar: rec.append('Use the closest historical incidents as evidence and validate any change against local change-management procedures.')
        return rec[:5]
