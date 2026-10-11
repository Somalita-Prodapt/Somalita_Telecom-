from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestRegressor
from src.utils.config import MODEL_PATH
FEATURES=['Cell Availability (%)','MTTR (hours)','Latency (ms)','Packet Loss Rate (%)','Call Drop Rate (%)','Handover Success Rate (%)','Alarm Count','Critical Alarm Count','Parameter Changes','Successful Configuration Changes (%)','Data Usage (GB)','User Count','Signal Strength (dBm)','Jitter (ms)','Connection Setup Success Rate (%)','Security Incidents','Authentication Failures','Temperature (°C)','Humidity (%)']
class PerformancePredictionAgent:
    def __init__(self,df,path=None):
        self.path=Path(path) if path else MODEL_PATH/'throughput_predictor.joblib'; self.path.parent.mkdir(parents=True,exist_ok=True)
        try:self.model=joblib.load(self.path)
        except Exception:self.model=None
        if self.model is None:
            self.model=RandomForestRegressor(n_estimators=100,max_depth=12,random_state=42,n_jobs=-1)
            self.model.fit(df[FEATURES].fillna(0),df['Throughput (Mbps)'].fillna(df['Throughput (Mbps)'].median())); joblib.dump(self.model,self.path)
    def predict(self,row):
        x=row[FEATURES].fillna(0).to_frame().T; p=float(self.model.predict(x)[0]); return {'predicted_throughput_mbps':round(p,2),'model':'RandomForestRegressor'}
