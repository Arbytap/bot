from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, companies, projects, sed, documents, approval

app = FastAPI(
    title="Project SED System",
    description="Корпоративная система электронного документооборота, ориентированная на проекты",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(projects.router)
app.include_router(sed.router)
app.include_router(documents.router)
app.include_router(approval.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
