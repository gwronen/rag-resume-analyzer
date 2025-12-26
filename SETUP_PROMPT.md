# Setup Instructions

## Step 2: Choose Your Setup Method

### Option A: Install Docker Desktop (Recommended - 5 minutes)

1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install Docker Desktop (follow the installer)
3. Start Docker Desktop
4. Once Docker is running, come back here and run:
   ```bash
   docker-compose up -d
   ```

### Option B: Manual Installation (More Complex)

#### For Prometheus:
1. Download from: https://prometheus.io/download/
2. Extract the zip file
3. Copy `prometheus.yml` to the extracted folder
4. Run: `prometheus.exe --config.file=prometheus.yml`

#### For Grafana:
1. Download from: https://grafana.com/grafana/download?platform=windows
2. Install Grafana
3. Start Grafana service
4. Open http://localhost:3000

## What's Next After Setup?

Once Prometheus and Grafana are running:

1. **Access Prometheus**: http://localhost:9090
   - Try query: `rag_questions_total`
   
2. **Access Grafana**: http://localhost:3000
   - Login: `admin` / `admin`
   - Add Prometheus datasource: http://localhost:9090

3. **Generate Metrics**: 
   - Start your Streamlit app: `streamlit run app.py`
   - Ask questions in the app
   - Watch metrics appear in Prometheus/Grafana!


