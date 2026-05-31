import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from db import engine, Base
from api import telemetry, evolution, auditor, evaluator

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Insurance-SuperSkill Platform",
    description="Insurance industry super-skill ecosystem platform server",
    version="1.0.0"
)

app.include_router(telemetry.router, prefix="/api/v1/telemetry", tags=["Telemetry"])
app.include_router(evolution.router, prefix="/api/v1/evolution", tags=["Evolution"])
app.include_router(auditor.router, prefix="/api/v1/auditor", tags=["Auditor"])
app.include_router(evaluator.router, prefix="/api/v1/evaluator", tags=["Evaluator"])

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def root():
    return {"message": "Insurance-SuperSkill Platform API", "version": "1.0.0"}

@app.get("/dashboard")
def dashboard():
    return FileResponse(os.path.join(static_dir, "dashboard.html"))
