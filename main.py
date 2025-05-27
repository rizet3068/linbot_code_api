from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel
from datetime import datetime
import subprocess
import os

app = FastAPI()

SAVE_DIR = "saved_codes"
os.makedirs(SAVE_DIR, exist_ok=True)

class CodeRequest(BaseModel):
    token: str
    code: str

SECRET_TOKEN = "lin-token-2025"

@app.post("/upload_code")
async def upload_code(data: CodeRequest):
    if data.token != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    filename = f"Linbot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    filepath = os.path.join(SAVE_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(data.code)

    return {"status": "success", "filename": filename}

@app.get("/download_code")
async def download_code(filename: str):
    filepath = os.path.join(SAVE_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=filepath, filename=filename, media_type="application/octet-stream")

@app.get("/list_files")
async def list_files():
    try:
        files = [f for f in os.listdir(SAVE_DIR) if f.endswith(".py")]
        return JSONResponse(content={"files": files})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read_file")
async def read_file(filename: str):
    filepath = os.path.join(SAVE_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return PlainTextResponse(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/run_code")
async def run_code(filename: str):
    filepath = os.path.join(SAVE_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        result = subprocess.run(["python", filepath], capture_output=True, text=True, timeout=5)
        return {"status": "success", "output": result.stdout or result.stderr}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
