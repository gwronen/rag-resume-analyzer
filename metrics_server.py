"""
Prometheus metrics server for RAG application.
This runs a Flask server on port 8000 to expose metrics.
"""
from flask import Flask
from prometheus_client import make_wsgi_app, Counter, Histogram, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Create Flask app
app = Flask(__name__)

# Prometheus metrics
rag_questions_total = Counter(
    'rag_questions_total',
    'Total number of questions asked',
    ['status']
)

rag_question_duration = Histogram(
    'rag_question_duration_seconds',
    'Time spent processing questions',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

rag_documents_loaded = Gauge(
    'rag_documents_loaded',
    'Number of documents in the index'
)

rag_chunks_created = Gauge(
    'rag_chunks_created',
    'Number of chunks created from documents'
)

rag_embeddings_generated = Counter(
    'rag_embeddings_generated_total',
    'Total number of embeddings generated'
)

rag_vector_search_duration = Histogram(
    'rag_vector_search_duration_seconds',
    'Time spent on vector similarity search',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
)

rag_llm_tokens = Counter(
    'rag_llm_tokens_total',
    'Total number of tokens used by LLM',
    ['type']  # 'prompt' or 'completion'
)

# Mount Prometheus metrics endpoint
app.wsgi_app = DispatcherMiddleware(
    app.wsgi_app,
    {'/metrics': make_wsgi_app()}
)

@app.route('/')
def index():
    return """
    <h1>RAG Application Metrics</h1>
    <p>Prometheus metrics are available at <a href="/metrics">/metrics</a></p>
    <h2>Available Metrics:</h2>
    <ul>
        <li><code>rag_questions_total</code> - Total questions asked</li>
        <li><code>rag_question_duration_seconds</code> - Question processing time</li>
        <li><code>rag_documents_loaded</code> - Number of documents in index</li>
        <li><code>rag_chunks_created</code> - Number of chunks</li>
        <li><code>rag_embeddings_generated_total</code> - Total embeddings</li>
        <li><code>rag_vector_search_duration_seconds</code> - Vector search time</li>
        <li><code>rag_llm_tokens_total</code> - LLM token usage</li>
    </ul>
    """

if __name__ == '__main__':
    print("Starting metrics server on http://localhost:8000")
    print("Metrics endpoint: http://localhost:8000/metrics")
    app.run(host='0.0.0.0', port=8000, debug=False)

