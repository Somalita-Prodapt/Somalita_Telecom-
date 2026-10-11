import pandas as pd
from pathlib import Path
from src.utils.config import DATASET_PATH, SAMPLE_DATASET_PATH, DATASET_SEARCH_DIR

REQUIRED_COLUMNS = [
    'Season','Cell Availability (%)','MTTR (hours)','Throughput (Mbps)','Latency (ms)',
    'Packet Loss Rate (%)','Call Drop Rate (%)','Handover Success Rate (%)','Alarm Count',
    'Critical Alarm Count','Parameter Changes','Successful Configuration Changes (%)','Data Usage (GB)',
    'User Count','Signal Strength (dBm)','Jitter (ms)','Connection Setup Success Rate (%)',
    'Security Incidents','Authentication Failures','Temperature (°C)','Humidity (%)','Weather',
    'Issue Reported','City','State','Zip','Fault Occurrence Rate (%)'
]
TEXT_COLUMNS = {'Season','Weather','Issue Reported','City','State'}


def load_dataset(path: Path | None = None) -> pd.DataFrame:
    target = path or DATASET_PATH
    if not target.exists():
        candidates = sorted(DATASET_SEARCH_DIR.glob('*.csv')) if DATASET_SEARCH_DIR.exists() else []
        if candidates:
            # Prefer the largest CSV in data/raw: this naturally selects the full 100K
            # dataset when it is present, without hard-coding a row count.
            target = max(candidates, key=lambda p: p.stat().st_size)
        elif SAMPLE_DATASET_PATH.exists():
            target = SAMPLE_DATASET_PATH
        else:
            raise FileNotFoundError(f'Dataset not found: {target}')
    df = pd.read_csv(target, low_memory=False)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f'Dataset missing required columns: {missing}')
    for c in df.columns:
        if c not in TEXT_COLUMNS:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=['Throughput (Mbps)', 'Latency (ms)']).reset_index(drop=True)
    df['incident_id'] = [f'NETOPS-{i+1:06d}' for i in range(len(df))]
    return df


def _fmt(v, digits=2):
    try:
        return f'{float(v):.{digits}f}'
    except Exception:
        return str(v)


def chunk_document(text: str, max_words: int = 180) -> list[str]:
    """Deterministic RAG chunking: short incident records remain one chunk; longer records split cleanly."""
    words = text.split()
    return [' '.join(words[i:i+max_words]) for i in range(0, len(words), max_words)] or ['']

def build_document(row) -> str:
    return (
        f"{row.get('Season', 0)} network incident in {row.get('City', 0)}, {row.get('State', 0)} (ZIP {row.get('Zip','N/A')}). "
        f"Issue reported: {row.get('Issue Reported', 0)}. Weather: {row.get('Weather', 0)}. "
        f"Availability {_fmt(row.get('Cell Availability (%)', 0))}%, MTTR {_fmt(row.get('MTTR (hours)', 0))} hours, "
        f"throughput {_fmt(row.get('Throughput (Mbps)', 0))} Mbps, latency {_fmt(row.get('Latency (ms)', 0))} ms, "
        f"packet loss {_fmt(row.get('Packet Loss Rate (%)', 0))}%, call drop {_fmt(row.get('Call Drop Rate (%)', 0))}%, "
        f"handover success {_fmt(row.get('Handover Success Rate (%)', 0))}%, alarms {_fmt(row.get('Alarm Count', 0),0)}, "
        f"critical alarms {_fmt(row.get('Critical Alarm Count', 0))}, parameter changes {_fmt(row.get('Parameter Changes', 0),0)}, "
        f"successful configuration changes {_fmt(row.get('Successful Configuration Changes (%)', 0))}%, "
        f"data usage {_fmt(row.get('Data Usage (GB)', 0))} GB, users {_fmt(row.get('User Count', 0),0)}, "
        f"signal {_fmt(row.get('Signal Strength (dBm)', 0))} dBm, jitter {_fmt(row.get('Jitter (ms)', 0))} ms, "
        f"connection setup success {_fmt(row.get('Connection Setup Success Rate (%)', 0))}%, "
        f"security incidents {_fmt(row.get('Security Incidents', 0),0)}, authentication failures {_fmt(row.get('Authentication Failures', 0),0)}, "
        f"temperature {_fmt(row.get('Temperature (°C)', 0))} °C, humidity {_fmt(row.get('Humidity (%)', 0))}%, "
        f"fault occurrence {_fmt(row.get('Fault Occurrence Rate (%)', 0))}%."
    )
