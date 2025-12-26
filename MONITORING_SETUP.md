# Monitoring Setup Guide

This guide explains how to set up Prometheus and Grafana monitoring for your RAG application.

## Architecture

- **Metrics Server** (Port 8000): Flask server exposing Prometheus metrics
- **Prometheus** (Port 9090): Time-series database collecting metrics
- **Grafana** (Port 3000): Visualization dashboard

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Metrics Server

In a terminal, run:
```bash
python metrics_server.py
```

This starts the Flask server on `http://localhost:8000` that exposes metrics.

### 3. Start Prometheus and Grafana

Using Docker Compose:
```bash
docker-compose up -d
```

Or manually:
```bash
# Start Prometheus
docker run -d -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus

# Start Grafana
docker run -d -p 3000:3000 -e GF_SECURITY_ADMIN_PASSWORD=admin grafana/grafana
```

### 4. Access the Services

- **Metrics Endpoint**: http://localhost:8000/metrics
- **Prometheus UI**: http://localhost:9090
- **Grafana UI**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`

### 5. Configure Grafana Dashboard

1. Log into Grafana at http://localhost:3000
2. Go to Configuration → Data Sources
3. Add Prometheus datasource:
   - URL: `http://prometheus:9090` (if using Docker) or `http://localhost:9090`
4. Import the dashboard from `grafana/dashboards/rag-dashboard.json`

## Metrics Available

### Counter Metrics
- `rag_questions_total` - Total number of questions asked (labeled by status)
- `rag_embeddings_generated_total` - Total embeddings generated

### Gauge Metrics
- `rag_documents_loaded` - Current number of documents in index
- `rag_chunks_created` - Current number of chunks

### Histogram Metrics
- `rag_question_duration_seconds` - Time spent processing questions
- `rag_vector_search_duration_seconds` - Time spent on vector similarity search

## Query Examples

### Total questions asked
```
sum(rag_questions_total)
```

### Questions per second
```
rate(rag_questions_total[5m])
```

### 95th percentile response time
```
histogram_quantile(0.95, rate(rag_question_duration_seconds_bucket[5m]))
```

### Success vs Error rate
```
sum by (status) (rag_questions_total)
```

## Stopping Services

```bash
# Stop Docker containers
docker-compose down

# Stop metrics server
# Press Ctrl+C in the terminal running metrics_server.py
```

## Troubleshooting

1. **Metrics not showing**: Make sure `metrics_server.py` is running on port 8000
2. **Prometheus can't scrape**: Check `prometheus.yml` configuration and ensure the metrics server is accessible
3. **Grafana can't connect to Prometheus**: Verify the Prometheus URL in Grafana datasource settings

