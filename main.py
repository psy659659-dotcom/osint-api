import os
import duckdb
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OSINT Phone Search API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_PARQUET = "hf://datasets/HiTeckGroup/HiTeckNuMinfo/users_data.parquet"

def get_connection():
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("SET enable_progress_bar=false;")
    return con

@app.get("/")
def root():
    return {"status": "ok", "message": "OSINT Phone Search API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/search")
def search(q: str, limit: int = 10):
    if not q or len(q) < 4:
        raise HTTPException(status_code=400, detail="Query too short")
    
    try:
        con = get_connection()
        query = f"""
            SELECT name, fname, mobile, alt, address, circle, id, email
            FROM read_parquet('{HF_PARQUET}')
            WHERE mobile = '{q}'
            LIMIT {limit}
        """
        result = con.execute(query).fetchall()
        columns = ["name", "fname", "mobile", "alt", "address", "circle", "id", "email"]
        rows = [dict(zip(columns, row)) for row in result]
        con.close()
        return {"query": q, "count": len(rows), "results": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
