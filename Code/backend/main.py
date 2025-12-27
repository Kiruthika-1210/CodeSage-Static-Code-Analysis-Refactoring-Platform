from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.analyze import router as analyze_router
from routes.ai_routes import router as ai_router
from routes.version_routes import router as version_router

from versions.versions import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # TEMPORARY — to confirm CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# Attach routers
app.include_router(analyze_router)
app.include_router(ai_router)
app.include_router(version_router)

@app.get("/")
def root():
    return {"message": "CodeSage Backend Running"}

@app.get("/health")
def health():
    return {"status": "ok"}
