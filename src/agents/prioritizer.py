class IncidentPrioritizerAgent:
    def prioritize(self, incidents):
        if not incidents: return {'priority':'LOW','score':0.0,'reason':'No incidents retrieved'}
        vals=[]
        for x in incidents:
            m=x['metadata']; s=0
            s += max(0,min(25,(100-float(m['Cell Availability (%)']))*1.2))
            s += max(0,min(25,float(m['Packet Loss Rate (%)'])*2))
            s += max(0,min(20,float(m['Call Drop Rate (%)'])*3))
            s += max(0,min(20,float(m['Critical Alarm Count'])*2))
            s += max(0,min(10,float(m['Fault Occurrence Rate (%)'])*0.3))
            vals.append(s)
        score=sum(vals)/len(vals); priority='CRITICAL' if score>=60 else 'HIGH' if score>=40 else 'MEDIUM' if score>=20 else 'LOW'
        return {'priority':priority,'score':round(score,2),'reason':'Composite severity from availability, packet loss, call drops, critical alarms and fault occurrence'}
