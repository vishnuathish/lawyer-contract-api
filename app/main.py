from fastapi import FastAPI
from contextlib import asynccontextmanager
try:
    from .database import init_db
    from .routes import contracts as contracts_router
    from .routes import analysis as analysis_router
except ImportError:
    from database import init_db
    from routes import contracts as contracts_router
    from routes import analysis as analysis_router

@asynccontextmanager
async def lifespan(_app: FastAPI):
    del _app
    init_db()
    yield

app = FastAPI(
    title="Lawer contracts API",
    description="AI-powered Contract analysis using Genimi",
    version="1.0.0",
    lifespan=lifespan,
)

#Root route 
@app.get("/")
async def root():
    return {
        "app": "Laywer contracts API",
        "version": "1.0.0",
        "endpoint": {
            "POST / contract/upload": "Upload a PDF or txt contract for analysis",
            "GET / contract/": "Retrive the list of all uploaded contracts",
            "GET /contract/{contract_id}": "Retrive the details of a specific contract by its ID",
            "POST /analysis/{contract_id}/analyze": "Analyze a contract using AI and return result insights",
        }
    }


app.include_router(contracts_router.router)
app.include_router(analysis_router.router)