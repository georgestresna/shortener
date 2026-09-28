import string
import random
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import RedirectResponse
import redis

app = FastAPI()
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.post("/api/shorten")
def shorten_url(payload: dict = Body(...)):
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Câmpul 'url' lipsește din JSON")
        
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