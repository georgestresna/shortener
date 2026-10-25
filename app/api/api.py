import string
import random
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.responses import RedirectResponse, JSONResponse
import redis
import os

import asyncio
from prometheus_fastapi_instrumentator import Instrumentator

#var mediu
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

ERROR_RATE = float(os.getenv("ERROR_RATE", "0"))
EXTRA_LATENCY_MS = int(os.getenv("EXTRA_LATENCY_MS", "0"))

app = FastAPI()

@app.middleware("http")
async def fault_injection(request: Request, call_next):
    if request.url.path in ("/health", "/ready", "/metrics"):
        return await call_next(request)
    if EXTRA_LATENCY_MS:
        await asyncio.sleep(EXTRA_LATENCY_MS / 1000)
    if ERROR_RATE and random.random() < ERROR_RATE:
        return JSONResponse({"error": "injected fault"}, status_code=500)
    return await call_next(request)

Instrumentator().instrument(app).expose(app, include_in_schema=False)


r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.post("/api/shorten", status_code=201)
def shorten_url(payload: dict = Body(...)):
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Campul 'url' lipsește din JSON")
        
    code = generate_code()
    
    # Previne coliziunile
    while r.exists(f"url:{code}"):
        code = generate_code()
        
    r.set(f"url:{code}", url)
    r.set(f"clicks:{code}", 0)
    return {"code": code}

@app.get("/r/{code}")
def redirect_url(code: str):
    url = r.get(f"url:{code}")
    if not url:
        raise HTTPException(status_code=404, detail="Link not found")
    
    r.incr(f"clicks:{code}")
    return RedirectResponse(url=url, status_code=307)

@app.get("/api/stats/{code}")
def get_stats(code: str):
    clicks = r.get(f"clicks:{code}")
    if clicks is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"clicks": int(clicks)}


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    r.ping()
    return {"status": "ready"}

# from prometheus_fastapi_instrumentator import Instrumentator
# Instrumentator().instrument(app).expose(app)