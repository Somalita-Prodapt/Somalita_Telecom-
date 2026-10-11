# 📡 Telecom NetOps AI Assistant — REST API Documentation

**API Title:** AI-Powered Telecom Network Operations Assistant  
**OpenAPI Specification:** OAS 3.1 (`/openapi.json`)  
**Base URL:** `http://127.0.0.1:8000`  
**Interactive Swagger UI:** `http://127.0.0.1:8000/docs`  
**ReDoc Specification:** `http://127.0.0.1:8000/redoc`  
**Version:** 3.0.0  

---

## Architecture & Authentication Overview
The Telecom NetOps API is an asynchronous REST microservice built on **FastAPI** and **Uvicorn**. It interfaces directly with the **Hybrid Retrieval Engine** (100,000 5G cell observations), the **Multi-Agent Cognitive Pipeline** (10 specialized micro-agents), and the **LLM RAG Synthesizer** (Anthropic Claude / OpenAI).

* **Protocol:** HTTP/1.1 (JSON payloads and CSV streaming attachments)
* **Authentication:** Local development / Enterprise Intranet (Secured via Ingress Guardrails and CORS)
* **Ingress Guardrails:** All queries are filtered for size ($1-1000$ chars), Regex XSS / injection attacks, and a 70+ keyword Telecom Domain Ontology filter. Out-of-domain queries return `HTTP 400 Bad Request`.

---

## API Endpoints Directory

| Category | HTTP Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **System & Health** | `GET` | `/health` | System liveness probe, model provider, and dataset row count |
| | `GET` | `/metadata` | Available states, cities, seasons, and conditions for UI filters |
| | `GET` | `/stats` | Whole-dataset telemetry aggregations and condition distributions |
| **Telemetry Search** | `POST` | `/search-incidents` | Hybrid BM25 + Dense vector search with metadata relaxation |
| | `GET` | `/incidents/{incident_id}` | Complete historical record lookup for a specific Cell Incident ID |
| | `POST` | `/search-incidents/export` | Stream full ranked search results directly as a CSV file |
| **AI Diagnosis** | `POST` | `/diagnose` | End-to-end 10-Agent diagnosis, ML predictions, and RAG dossier |
| **Human Feedback** | `POST` | `/feedback` | Submit operator relevance ratings (1–5 stars) and audit notes |
| | `GET` | `/feedback/summary` | Aggregate feedback statistics and average rating |
| | `GET` | `/feedback/recent` | List latest operator feedback submissions |
| **Dataset Explorer**| `GET` | `/dataset/options` | Retrieve available Circle, Severity, Season, and Issue filters |
| | `GET` | `/dataset` | Server-side paginated and sorted exploration over 100,000 cells |
| | `GET` | `/dataset/export` | Stream full filtered dataset records as a CSV file |
| **Evaluation Hub** | `POST` | `/evaluate/retrieval` | Execute Hit@k keyword retrieval test suite over 100K rows |
| | `GET` / `POST` | `/evaluate/ragas` | Run or retrieve RAGAS generation benchmark metrics |
| | `GET` / `POST` | `/evaluate/deepeval`| Run or retrieve DeepEval assertion test suite |

---

## 1. System & Health Endpoints

### `GET /health`
Liveness probe providing real-time operational status, configured model, and loaded dataset size.

* **Response (`200 OK`):**
```json
{
  "status": "ok",
  "service": "AI-Powered Telecom Network Operations Assistant",
  "version": "3.0.0",
  "incident_count": 100000,
  "semantic_embeddings_configured": false,
  "demo_mode": false,
  "claude_configured": true,
  "openai_configured": false,
  "llm_provider": "anthropic (claude-sonnet-4-5-20250929)",
  "semantic_retrieval_status": "initializes on first search; TF-IDF semantic fallback is available",
  "message": "API process is healthy"
}
```

* **cURL Example:**
```bash
curl -X GET "http://127.0.0.1:8000/health"
```

---

### `GET /metadata`
Returns unique categorical values present in the loaded dataset for frontend filter dropdowns.

* **Response (`200 OK`):**
```json
{
  "incident_count": 100000,
  "states": ["Alabama", "Alaska", "Arizona", "..."],
  "cities": ["Austinport", "Lake Justinmouth", "North Paulton", "..."],
  "seasons": ["Fall", "Spring", "Summer", "Winter"],
  "weather": ["Clear", "Cloudy", "Rainy", "Snowy", "Windy"],
  "network_conditions": ["Healthy", "At Risk", "Degraded"]
}
```

---

### `GET /stats`
Computes aggregate statistical telemetry across all 100,000 records.

* **Response (`200 OK`):**
```json
{
  "incident_count": 100000,
  "avg_latency_ms": 79.22,
  "avg_throughput_mbps": 586.57,
  "avg_packet_loss_pct": 6.46,
  "avg_fault_occurrence_pct": 38.16,
  "high_risk_rows": 28412,
  "network_condition_counts": {
    "Healthy": 48200,
    "Degraded": 32100,
    "At Risk": 19700
  },
  "season_counts": {
    "Winter": 25100,
    "Summer": 24900,
    "Fall": 25050,
    "Spring": 24950
  }
}
```

---

## 2. Telemetry Search Endpoints

### `POST /search-incidents`
Executes hybrid search (BM25 + Dense Sentence Transformers) across the 100,000 incident dataset with optional metadata filtering and nearest-match relaxation.

* **Query Parameters:**
  * `page` (optional, integer, default: `1`): Results page index.
  * `page_size` (optional, integer, default: `500`, max: `1000`): Items per page.

* **Request Body (`SearchRequest`):**
```json
{
  "query": "A cell is experiencing high latency, packet loss and reduced throughput",
  "top_k": 5,
  "state": "Texas",
  "city": null,
  "season": "Winter",
  "weather": null,
  "network_condition": "Degraded"
}
```

* **Response (`200 OK`):**
```json
{
  "query": "A cell is experiencing high latency, packet loss and reduced throughput",
  "filters": {
    "state": "Texas",
    "city": null,
    "season": "Winter",
    "weather": null,
    "network_condition": "Degraded"
  },
  "results": [
    {
      "incident_id": "NETOPS-002743",
      "score": 0.06012,
      "semantic_score": 0.0543,
      "lexical_score": 0.0412,
      "bm25_score": 0.0784,
      "metadata": {
        "Cell ID": "CELL-4892",
        "City": "North Paulton",
        "State": "Texas",
        "Latency (ms)": 90.49,
        "Packet Loss Rate (%)": 9.59,
        "Throughput (Mbps)": 494.45,
        "Cell Availability (%)": 98.82,
        "Critical Alarm Count": 7
      },
      "document": "Winter network incident in North Paulton, Texas... Latency 90.49 ms, Packet Loss 9.59%..."
    }
  ],
  "match_mode": "exact",
  "relaxed_filters": [],
  "filter_diagnostics": {
    "total_incidents": 100000,
    "selected_filters": {
      "State": "Texas",
      "Season": "Winter",
      "Network Condition": "Degraded"
    },
    "exact_match_count": 842
  },
  "total_results": 842,
  "page": 1,
  "page_size": 500,
  "retrieval_scope": "entire filtered dataset",
  "display_limit": 5
}
```

* **cURL Example:**
```bash
curl -X POST "http://127.0.0.1:8000/search-incidents" \
  -H "Content-Type: application/json" \
  -d '{"query": "high latency and packet loss", "top_k": 5}'
```

---

### `GET /incidents/{incident_id}`
Retrieves all 27 telemetry attributes for a single incident record by ID.

* **Path Parameters:**
  * `incident_id` (string, required): e.g. `NETOPS-002743`

* **Response (`200 OK`):**
```json
{
  "incident_id": "NETOPS-002743",
  "metadata": {
    "Season": "Winter",
    "Cell Availability (%)": 98.82,
    "MTTR (hours)": 4.2,
    "Throughput (Mbps)": 494.45,
    "Latency (ms)": 90.49,
    "Packet Loss Rate (%)": 9.59,
    "Call Drop Rate (%)": 1.45,
    "Handover Success Rate (%)": 95.12,
    "Alarm Count": 14,
    "Critical Alarm Count": 7,
    "Signal Strength (dBm)": -98.2,
    "Jitter (ms)": 14.1,
    "City": "North Paulton",
    "State": "Texas",
    "Fault Occurrence Rate (%)": 41.77
  }
}
```

* **Error Response (`404 Not Found`):**
```json
{
  "detail": "Incident not found"
}
```

---

### `POST /search-incidents/export`
Exports every record matching the search query and filters as a streaming CSV download.

* **Headers Returned:**
  * `Content-Type: text/csv`
  * `Content-Disposition: attachment; filename=netops_search_evidence.csv`

---

## 3. Multi-Agent AI Diagnosis Endpoints

### `POST /diagnose`
Executes end-to-end cognitive diagnosis coordinating the 10 micro-agents, ML regressors, and Claude RAG synthesis.

* **Request Body (`DiagnosisRequest`):**
```json
{
  "query": "A cell is experiencing high latency, packet loss and reduced throughput. Find similar historical incidents and recommend corrective actions.",
  "top_k": 5,
  "state": null,
  "city": null,
  "season": null,
  "weather": null,
  "network_condition": null,
  "include_predictions": true
}
```

* **Response Structure (`200 OK`):**
```json
{
  "status": "ok",
  "query": "A cell is experiencing high latency, packet loss and reduced throughput...",
  "classification": {
    "category": "packet_loss",
    "confidence": 0.79,
    "evidence": ["high_latency", "packet_loss", "congestion"]
  },
  "prioritization": {
    "priority": "HIGH",
    "score": 55.18,
    "reason": "Composite severity from availability, packet loss, call drops, critical alarms and fault occurrence"
  },
  "risk_prediction": {
    "risk_probability": 0.0741,
    "risk_level": "LOW",
    "model": "RandomForestClassifier"
  },
  "performance_prediction": {
    "predicted_throughput_mbps": 724.68,
    "model": "RandomForestRegressor"
  },
  "root_cause": {
    "primary_cause": "packet_loss_or_link_quality",
    "confidence": 0.90,
    "contributing_factors": ["critical_alarm_condition"]
  },
  "network_impact": {
    "impact_level": "MEDIUM",
    "effects": [
      "higher user-perceived response time",
      "retransmissions and degraded data sessions"
    ]
  },
  "recommendations": [
    "Check radio/transport link quality, retransmissions, packet-error counters and congestion indicators",
    "Review utilization, transport latency and traffic distribution against healthy peer cells",
    "Monitor handover success, fault occurrence, and packet loss against pre-change baseline"
  ],
  "rag_answer": {
    "answer": "# Telecom NOC Decision-Support Assessment\n\n## Incident Overview...",
    "model": "claude-sonnet-4-5-20250929",
    "tokens": 482
  },
  "similar_incidents": [
    {
      "incident_id": "NETOPS-002743",
      "score": 0.06012,
      "metadata": { "..." : "..." }
    }
  ],
  "evidence_summary": "Whole-dataset evidence: 100,000 matching historical observation(s). Latency: min=4.62, mean=79.22, max=175.84...",
  "whole_dataset_match_count": 100000,
  "match_mode": "exact"
}
```

* **cURL Example:**
```bash
curl -X POST "http://127.0.0.1:8000/diagnose" \
  -H "Content-Type: application/json" \
  -d '{"query": "A cell is experiencing high latency, packet loss and low throughput", "top_k": 5}'
```

---

## 4. Human-in-the-Loop Feedback Endpoints

### `POST /feedback`
Stores operator evaluations and notes in persistent SQLite/JSON storage for continuous model auditability.

* **Request Body (`FeedbackRequest`):**
```json
{
  "query": "high latency and packet loss",
  "incident_id": "NETOPS-002743",
  "rating": 5,
  "comment": "Accurately identified transport queue bottleneck."
}
```

* **Response (`200 OK`):**
```json
{
  "status": "ok",
  "message": "Feedback recorded successfully",
  "feedback_id": "fb_173926514"
}
```

---

### `GET /feedback/summary`
Returns aggregate user ratings and total feedback submissions count.

* **Response (`200 OK`):**
```json
{
  "total_feedback": 48,
  "average_rating": 4.65,
  "ratings_distribution": {
    "5": 34,
    "4": 11,
    "3": 2,
    "2": 1,
    "1": 0
  }
}
```

---

### `GET /feedback/recent?limit=50`
Lists recent operator feedback entries.

* **Query Parameters:**
  * `limit` (integer, default: `50`, min: `1`, max: `200`): Maximum entries to return.

---

## 5. Dataset Explorer Endpoints

### `GET /dataset/options`
Returns unique metadata filter choices available in the Dataset Explorer.

* **Response (`200 OK`):**
```json
{
  "circle": ["Austinport", "Lake Justinmouth", "North Paulton", "..."],
  "severity": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
  "season": ["Fall", "Spring", "Summer", "Winter"],
  "issue_type": ["Backhaul", "Coverage Gap", "Dropped Calls", "Handover Failures", "Interference", "Packet Loss"],
  "total_count": 100000
}
```

---

### `GET /dataset`
Server-side paginated and sorted explorer operating across the full 100,000-record dataset.

* **Query Parameters:**
  * `circle` (string, optional)
  * `severity` (string, optional: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`)
  * `season` (string, optional: `Fall`, `Spring`, `Summer`, `Winter`)
  * `issue_type` (string, optional: `Backhaul`, `Coverage Gap`, `Dropped Calls`, etc.)
  * `sort_by` (string, default: `Highest Risk`): Choices: `Highest Risk`, `Lowest Risk`, `Highest Fault Occurrence`, `Lowest Handover Success`, `Highest Latency`, `Highest Throughput`.
  * `page` (integer, default: `1`)
  * `page_size` (integer, default: `500`, max: `1000`)

* **Response (`200 OK`):**
```json
{
  "total_count": 100000,
  "filtered_count": 14250,
  "columns": ["Season", "Cell Availability (%)", "Throughput (Mbps)", "Latency (ms)", "Risk Index", "Severity", "Issue Type", "..."],
  "rows": [ { "...": "..." } ],
  "filters": { "Severity": "critical" },
  "sort_by": "Highest Risk",
  "page": 1,
  "page_size": 500,
  "page_count": 29,
  "retrieval_scope": "entire loaded dataset"
}
```

---

### `GET /dataset/export`
Exports all records matching the Dataset Explorer filters as a downloadable CSV.

---

## 6. Evaluation & Benchmark Endpoints

### `POST /evaluate/retrieval`
Executes automated Hit@k evaluation against `evaluation/test_cases.json` over the full 100,000 dataset.

* **Response (`200 OK`):**
```json
{
  "hit_rate": 1.0,
  "cases": [
    {
      "query": "high latency packet loss reduced throughput",
      "hit@k": true,
      "returned": 5,
      "top_score": 0.07226
    },
    {
      "query": "poor signal and dropped calls",
      "hit@k": true,
      "returned": 5,
      "top_score": 0.03556
    },
    {
      "query": "handover failures and fault occurrence",
      "hit@k": true,
      "returned": 5,
      "top_score": 0.08827
    },
    {
      "query": "increasing critical alarms",
      "hit@k": true,
      "returned": 5,
      "top_score": 0.04150
    }
  ]
}
```

---

### `GET` / `POST /evaluate/ragas`
Runs or retrieves RAGAS benchmark scores (Faithfulness, Relevancy, Context Precision).

* **Query Parameters:**
  * `run_live` (boolean, default: `false`): If `true` and OpenAI key is configured, triggers a live RAGAS evaluation execution.

* **Response (`200 OK`):**
```json
{
  "summary": {
    "faithfulness": 0.88,
    "response_relevancy": 0.93,
    "context_precision": 0.90,
    "mode": "RAGAS benchmark pipeline"
  },
  "samples": [
    {
      "query": "High latency, packet loss and reduced throughput",
      "contexts_retrieved": 5,
      "faithfulness": 0.88,
      "response_relevancy": 0.93,
      "context_precision": 0.90
    }
  ]
}
```

---

### `GET` / `POST /evaluate/deepeval`
Runs or retrieves DeepEval unit test assertion metrics.

* **Response (`200 OK`):**
```json
{
  "summary": {
    "total_test_cases": 2,
    "passed_test_cases": 2,
    "pass_rate": 1.0,
    "avg_relevancy": 0.96,
    "avg_faithfulness": 0.98,
    "mode": "DeepEval test harness"
  },
  "cases": [
    {
      "input_query": "A cell is experiencing high latency, packet loss and reduced throughput",
      "answer_relevancy": 0.96,
      "faithfulness": 0.98,
      "threshold": 0.5,
      "status": "PASSED"
    }
  ]
}
```

---

## 7. Error Codes & Validation Schemas

### Standard HTTP Status Codes

| Code | Name | Meaning | Common Cause |
| :--- | :--- | :--- | :--- |
| `200` | OK | Request succeeded | Valid operational inquiry |
| `400` | Bad Request | Guardrail or validation failure | Non-telecom inquiry, `<script>` injection, or blank query |
| `404` | Not Found | Resource does not exist | Incident ID not found in dataset |
| `422` | Unprocessable Entity | Pydantic schema validation error | Missing required fields or incorrect data types |
| `500` | Internal Server Error | Unhandled server error | Fatal runtime error (handled via fallback) |

### Validation Error Schema (`HTTPValidationError`)
```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Ingress Guardrail Rejection (`HTTP 400 Bad Request`)
```json
{
  "detail": "Out-of-domain query rejected: Request contains no recognizable telecom network terminology."
}
```
