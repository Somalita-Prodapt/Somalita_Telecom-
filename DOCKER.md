# Docker deployment

1. Copy `.env.example` to `.env` and adjust dataset/model options.
2. Ensure `data/raw/5G_netops_data_100K.csv` exists, or run `python scripts/download_dataset.py` before building.
3. Run `docker compose up --build`.
4. Open Streamlit at `http://localhost:8501` and API docs at `http://localhost:8000/docs`.

The dataset and storage folders are mounted so the source dataset and persistent artifacts remain outside the containers. For production, add authentication, secrets management, resource limits, and an organization-approved reverse proxy.
