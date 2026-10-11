import re
class IncidentClassifierAgent:
    categories={
      'high_latency': ['latency','slow response','delay'],
      'packet_loss': ['packet loss','loss'],
      'congestion': ['congestion','reduced throughput','low throughput','capacity'],
      'signal_quality': ['signal','poor coverage','weak signal'],
      'handover_failure': ['handover','handoff'],
      'service_degradation': ['degradation','poor service','quality'],
      'alarm_spike': ['alarm','critical alarm'],
      'fault': ['fault','failure','outage']}
    def classify(self,query):
        q=query.lower(); scores={k:sum(1 for x in terms if re.search(r'\b'+re.escape(x)+r'\b',q)) for k,terms in self.categories.items()}
        best=max(scores,key=scores.get); raw=scores[best]
        if raw==0: best='general_network_issue'; conf=0.35
        else: conf=min(0.98,0.55+0.12*raw)
        return {'category':best,'confidence':round(conf,3),'evidence':[k for k,v in scores.items() if v>0]}
