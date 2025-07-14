from fastapi import FastAPI, Request, Response, HTTPException
import os

APP_ID = os.getenv("X_APPLICATION_ID")        
if not APP_ID:
    raise RuntimeError("Falta X_APPLICATION_ID")

app = FastAPI(root_path="/api/rappi-connect-dev")  
HDR = "x_application_id"

@app.middleware("http")
async def require_app_id(request: Request, call_next):
    if request.headers.get(HDR, APP_ID) != APP_ID:
        raise HTTPException(400, f"Valor inválido de {HDR}")
    resp: Response = await call_next(request)
    resp.headers[HDR] = APP_ID
    return resp

@app.get("/health")                     
async def health():
    return {"status": "ok"}
