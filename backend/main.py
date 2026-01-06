from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, generate_latest

import time


app = FastAPI()

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency",
    ["endpoint"]
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    REQUEST_COUNT.labels(
        request.method,
        request.url.path,
        response.status_code
    ).inc()

    REQUEST_LATENCY.labels(request.url.path).observe(duration)
    return response


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return generate_latest()
