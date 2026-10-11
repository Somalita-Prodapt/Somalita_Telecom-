from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestClassifier
from src.utils.config import MODEL_PATH
FEATURES=['Cell Availability (%)','MTTR (hours)','Throughput (Mbps)','Latency (ms)','Packet Loss Rate (%)','Call Drop Rate (%)','Handover Success Rate (%)','Alarm Count','Critical Alarm Count','Parameter Changes','Successful Configuration Changes (%)','Data Usage (GB)','User Count','Signal Strength (dBm)','Jitter (ms)','Connection Setup Success Rate (%)','Security Incidents','Authentication Failures','Temperature (°C)','Humidity (%)']

class FaultRiskAgent:
    def __init__(self, df, path=None):
        self.path=Path(path) if path else MODEL_PATH/'fault_risk.joblib'; self.path.parent.mkdir(parents=True,exist_ok=True)
        self.model=None; self.constant_probability=None
        y=(df['Fault Occurrence Rate (%)']>=50).astype(int)
        if y.nunique()<2:
            # The small bundled demo fixture may contain only one class; keep the app runnable.
            self.constant_probability=float(y.mean())
            return
        try:self.model=joblib.load(self.path)
        except Exception:self.model=None
        if self.model is None:
            X=df[FEATURES].fillna(0)
            self.model=RandomForestClassifier(n_estimators=120,max_depth=10,random_state=42,n_jobs=-1,class_weight='balanced')
            self.model.fit(X,y); joblib.dump(self.model,self.path)
    def predict(self,row):
        if self.constant_probability is not None:
            # Conservative heuristic fallback for demo data without both risk classes.
            p=0.10
            p += min(0.30,max(0,(100-float(row['Cell Availability (%)']))/100))
            p += min(0.25,max(0,float(row['Packet Loss Rate (%)'])/40))
            p += min(0.20,max(0,float(row['Call Drop Rate (%)'])/10))
            p += min(0.15,max(0,float(row['Critical Alarm Count'])/40))
            p=min(.99,p)
            return {'risk_probability':round(p,4),'risk_level':'HIGH' if p>=.67 else 'MEDIUM' if p>=.33 else 'LOW','model':'heuristic demo fallback'}
        x=row[FEATURES].fillna(0).to_frame().T; p=float(self.model.predict_proba(x)[0,1])
        return {'risk_probability':round(p,4),'risk_level':'HIGH' if p>=.67 else 'MEDIUM' if p>=.33 else 'LOW','model':'RandomForestClassifier'}
