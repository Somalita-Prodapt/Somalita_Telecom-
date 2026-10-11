# Dataset Details

## Dataset name
5G Network Operations (NetOps) Dataset

## Primary source
Hugging Face: https://huggingface.co/datasets/fenar/5g_netops

## Alternative source
RANalyzer Dataset: https://github.com/wineslab/RANalyzer-Dataset

## Format
CSV; the primary source provides the dataset compressed as XZ.

## Purpose
Historical telecom network operations and performance information for semantic incident retrieval, hybrid search, incident classification, fault-risk prediction, performance prediction, root-cause analysis, troubleshooting recommendations and network-operations decision support.

## Key fields
Season, Cell Availability (%), MTTR (hours), Throughput (Mbps), Latency (ms), Packet Loss Rate (%), Call Drop Rate (%), Handover Success Rate (%), Alarm Count, Critical Alarm Count, Parameter Changes, Successful Configuration Changes (%), Data Usage (GB), User Count, Signal Strength (dBm), Jitter (ms), Connection Setup Success Rate (%), Security Incidents, Authentication Failures, Temperature (°C), Humidity (%), Weather, Issue Reported, City, State, Zip and Fault Occurrence Rate (%).

## Preprocessing
1. Validate all required columns.
2. Convert numeric fields safely with coercion.
3. Remove records missing core throughput/latency values.
4. Create deterministic incident IDs.
5. Convert each row into an evidence-rich incident document.
6. Build a TF-IDF lexical index.
7. Optionally encode documents using SentenceTransformer embeddings and persist them in ChromaDB.
8. Apply metadata filters before final ranking.
9. Keep the original row metadata in API results for traceability.

## Demo data
A small CSV fixture is included for offline demonstration and automated tests. It is not claimed to be the full 100,000-row dataset. Run `python scripts/download_dataset.py` for the official dataset.
