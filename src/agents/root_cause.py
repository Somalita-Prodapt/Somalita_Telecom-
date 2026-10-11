class RootCauseAgent:
    def analyze(self,row,classification):
        m=row; causes=[]
        if float(m['Latency (ms)'])>100: causes.append(('latency_pressure',0.9))
        if float(m['Packet Loss Rate (%)'])>8: causes.append(('packet_loss_or_link_quality',0.9))
        if float(m['Throughput (Mbps)'])<400: causes.append(('capacity_or_congestion',0.75))
        if float(m['Signal Strength (dBm)'])<-105: causes.append(('weak_radio_signal',0.85))
        if float(m['Handover Success Rate (%)'])<93: causes.append(('handover_instability',0.8))
        if float(m['Critical Alarm Count'])>=7: causes.append(('critical_alarm_condition',0.85))
        if float(m['Authentication Failures'])>=30: causes.append(('authentication_instability',0.7))
        if not causes: causes=[('no_single_dominant_cause_detected',0.4)]
        causes=sorted(causes,key=lambda x:-x[1])
        return {'primary_cause':causes[0][0],'confidence':causes[0][1],'contributing_factors':[x[0] for x in causes[1:5]]}

class NetworkImpactAgent:
    def analyze(self,row):
        impact=[]
        if float(row['Latency (ms)'])>80: impact.append('higher user-perceived response time')
        if float(row['Packet Loss Rate (%)'])>5: impact.append('retransmissions and degraded data sessions')
        if float(row['Call Drop Rate (%)'])>2: impact.append('voice service quality degradation')
        if float(row['Handover Success Rate (%)'])<94: impact.append('mobility/session continuity risk')
        if float(row['Cell Availability (%)'])<90: impact.append('reduced service availability')
        return {'impact_level':'HIGH' if len(impact)>=3 else 'MEDIUM' if impact else 'LOW','effects':impact}
