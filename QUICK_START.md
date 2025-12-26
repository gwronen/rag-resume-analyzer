# Quick Start Guide - Monitoring Setup

## Step 1: Install Python Dependencies

First, install the new monitoring packages:

```bash
pip install -r requirements.txt
```

This installs:
- `prometheus-client` - For exposing metrics
- `flask` - For the metrics server

## Step 2: Start the Metrics Server

**Open a NEW terminal window** and run:

```bash
python metrics_server.py
```

You should see:
```
Starting metrics server on http://localhost:8000
Metrics endpoint: http://localhost:8000/metrics
```

**Keep this terminal open!** The metrics server needs to keep running.

## Step 3: Choose Your Setup Option

### Option A: Using Docker (Recommended - Easier)

**Prerequisites:** Install Docker Desktop from https://www.docker.com/products/docker-desktop

Once Docker is installed, run:
```bash
docker-compose up -d
```

This starts:
- Prometheus on http://localhost:9090
- Grafana on http://localhost:3000

### Option B: Manual Setup (Without Docker)

#### Start Prometheus:

Download Prometheus from https://prometheus.io/download/
Extract it and run:
```bash
prometheus --config.file=prometheus.yml
```

#### Start Grafana:

Download Grafana from https://grafana.com/grafana/download
Install and start the service, then open http://localhost:3000

## Step 4: Access the Dashboards

1. **Metrics Endpoint**: http://localhost:8000/metrics
   - Should show all your Prometheus metrics in text format

2. **Prometheus UI**: http://localhost:9090
   - Try querying: `rag_questions_total`
   - Explore the Graph tab

3. **Grafana UI**: http://localhost:3000
   - Login: `admin` / `admin`
   - Go to Configuration → Data Sources
   - Add Prometheus: URL = `http://localhost:9090`
   - Import dashboard from `grafana/dashboards/rag-dashboard.json`

## Step 5: Generate Some Metrics!

**In another terminal**, start your Streamlit app:

```bash
streamlit run app.py
```

Then ask some questions in the app! Each question will generate metrics that you can see in:
- Prometheus (real-time queries)
- Grafana (beautiful dashboards)

## What to Expect

Once you ask questions in your Streamlit app, you should see:
- ✅ `rag_questions_total` incrementing
- ✅ `rag_question_duration_seconds` showing response times
- ✅ `rag_vector_search_duration_seconds` showing search performance
- ✅ Charts and graphs in Grafana updating in real-time

## Troubleshooting

**Metrics not appearing?**
- Make sure `metrics_server.py` is running (Step 2)
- Make sure your Streamlit app is using the updated `main.py` with metrics
- Check http://localhost:8000/metrics to see if metrics are being exposed

**Prometheus can't scrape?**
- Check that metrics_server.py is running on port 8000
- Verify prometheus.yml has the correct target: `localhost:8000`

**Need help?** Check `MONITORING_SETUP.md` for detailed documentation.

