from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import clients, campaigns, upload, jobs

app = FastAPI(title="Finautomation", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router, prefix="/api", tags=["Clients"])
app.include_router(campaigns.router, prefix="/api", tags=["Campaigns"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
