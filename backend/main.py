# backend/main.py
import logging
import time
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile, Query, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pymongo import MongoClient
from pymongo.database import Database

from . import config, services, models, ml_model

# Khởi tạo và Cấu hình 
app = FastAPI(title="Polyvore Backend with MongoDB Atlas", version="6.0.0-structured")
logger = logging.getLogger("polyvore-backend")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")

# Connect Database 
mongo_client: Optional[MongoClient] = None
db: Optional[Database] = None

def get_database() -> Database:
    if db is None:
        raise RuntimeError("Database connection not established.")
    return db

# Application Lifecycle
@app.on_event("startup")
def startup_event():
    global mongo_client, db
    logger.info("--- Connecting to MongoDB Atlas... ---")
    mongo_client = MongoClient(config.MONGO_URI)
    db = mongo_client[config.DB_NAME]
    try:
        mongo_client.admin.command('ping')
        logger.info("--- MongoDB connection successful! ---")
    except Exception as e:
        logger.error(f"--- MongoDB connection failed: {e} ---")
        raise RuntimeError(f"Could not connect to MongoDB: {e}")
    
    logger.info("--- Loading ML Model... ---")
    ml_model.load_model()

@app.on_event("shutdown")
def shutdown_event():
    if mongo_client:
        mongo_client.close()
        logger.info("--- MongoDB connection closed. ---")

#  Middleware 
app.add_middleware(
    CORSMiddleware, allow_origins=config.ORIGINS, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1024)

@app.middleware("http")
async def add_timing(request, call_next):
    t0 = time.time()
    resp = await call_next(request)
    ms = (time.time() - t0) * 1000
    logger.info("%s %s -> %d (%.1f ms)", request.method, request.url.path, resp.status_code, ms)
    return resp

# API Endpoints 
@app.get("/healthz")
def healthz(db: Database = Depends(get_database)):
    try:
        model_status = "loaded" if ml_model.get_model() else "not loaded"
        db_collections = db.list_collection_names()
        return {"status": "ok", "model_status": model_status, "database_connection": "ok", "collections": db_collections}
    except Exception as e:
        raise HTTPException(503, f"Health check failed: {e}")

@app.post("/similar/{item_id}", response_model=models.SearchResponse, summary="Find similar items using MongoDB")
async def similar_endpoint(item_id: str, topk: int = Query(10, ge=1, le=50), candidates: int = Query(100, ge=10, le=500), db: Database = Depends(get_database)):
    response = await services.find_similar_by_id(item_id, topk, candidates, db)
    if response is None:
        raise HTTPException(404, f"Item or embedding for {item_id} not found")
    return response

@app.post("/search_image", response_model=models.SearchResponse, summary="Find similar items by image using MongoDB")
async def search_image_endpoint(file: UploadFile = File(...), topk: int = Query(10, ge=1, le=50), candidates: int = Query(100, ge=10, le=500), db: Database = Depends(get_database)):
    return await services.find_similar_by_image(file, topk, candidates, db)

@app.post("/compatible/{item_id}", response_model=models.SearchResponse, summary="Get compatible items using pre-computed mapping")
async def compatible_endpoint(item_id: str, db: Database = Depends(get_database)):
    return await services.get_compatible_items(item_id, db)

@app.get("/image/{item_id}", summary="Get product image by item_id")
async def image_endpoint(item_id: str, db: Database = Depends(get_database)):
    image_binary, media_type = await services.get_image_binary(item_id, db)
    if not image_binary:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=image_binary, media_type=media_type)