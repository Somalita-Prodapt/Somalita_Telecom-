from src.rag.preprocessing import build_document
def test_document():
    row={'Season':'Winter','City':'Test','State':'TS','Issue Reported':'yes','Weather':'Clear','Cell Availability (%)':99,'Throughput (Mbps)':500,'Latency (ms)':50,'Packet Loss Rate (%)':2,'Call Drop Rate (%)':1,'Handover Success Rate (%)':97,'Alarm Count':2,'Critical Alarm Count':1,'Signal Strength (dBm)':-80,'Jitter (ms)':5,'User Count':1000,'Fault Occurrence Rate (%)':10}
    assert 'Test' in build_document(row)
