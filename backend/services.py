# backend/services.py
import io
import logging
from typing import List, Tuple
from PIL import Image
from fastapi import UploadFile
from pymongo.database import Database

from . import config, ml_model, models

logger = logging.getLogger("polyvore-backend")

# Feature 1: Tìm kiếm tương tự ( find similar items )

def _perform_mongo_vector_search(db: Database, query_vector: list, topk: int, candidates: int) -> List[dict]:
    """Hàm lõi thực hiện truy vấn $vectorSearch và join với Metadata."""
    pipeline = [
        {"$vectorSearch": {"index": "default", "path": "embedding", "queryVector": query_vector, "numCandidates": candidates, "limit": topk}},
        {"$lookup": {"from": config.METADATA_COLLECTION, "localField": "item_id", "foreignField": "item_id", "as": "metadata"}},
        {"$match": {"metadata": {"$ne": []}}},
        {"$project": {"_id": 0, "item_id": 1, "score": {"$meta": "vectorSearchScore"}, "title": {"$arrayElemAt": ["$metadata.title", 0]}, "main_category": {"$arrayElemAt": ["$metadata.main_category", 0]}, "sub_category": {"$arrayElemAt": ["$metadata.subcategory", 0]}}}
    ]
    return list(db[config.EMBEDDINGS_COLLECTION].aggregate(pipeline))

async def find_similar_by_id(item_id: str, topk: int, candidates: int, db: Database) -> models.SearchResponse:
    """Tìm sản phẩm tương tự dựa trên item_id."""
    doc = db[config.EMBEDDINGS_COLLECTION].find_one({"item_id": item_id})
    if not doc or "embedding" not in doc:
        return None
    search_results = _perform_mongo_vector_search(db, doc["embedding"], topk, candidates)
    return models.SearchResponse(results=search_results)

async def find_similar_by_image(file: UploadFile, topk: int, candidates: int, db: Database) -> models.SearchResponse:
    """Tìm sản phẩm tương tự dựa trên file ảnh."""
    content = await file.read()
    img = Image.open(io.BytesIO(content))
    query_vector = ml_model.image_to_vec(img)
    search_results = _perform_mongo_vector_search(db, query_vector, topk, candidates)
    return models.SearchResponse(results=search_results)

# Feature 2: Gợi ý phối đồ ( get compatible items )

async def get_compatible_items(item_id: str, db: Database) -> models.SearchResponse:
    """Lấy các sản phẩm gợi ý phối đồ."""
    mapping_doc = db[config.OUTFIT_MAPPING_COLLECTION].find_one({"item_id": item_id})
    if not mapping_doc or "rec_feature2" not in mapping_doc or not mapping_doc["rec_feature2"]:
        logger.warning(f"No compatibility mapping found for item_id: {item_id}")
        return models.SearchResponse(results=[])

    recommended_ids = mapping_doc["rec_feature2"]
    pipeline = [
        {"$match": {"item_id": {"$in": recommended_ids}}},
        {"$project": {"_id": 0, "item_id": 1, "title": 1, "main_category": 1, "sub_category": "$subcategory"}}
    ]
    metadata_docs = list(db[config.METADATA_COLLECTION].aggregate(pipeline))
    results = [dict(doc, score=1.0) for doc in metadata_docs]
    return models.SearchResponse(results=results)

# Feature 3: Lấy ảnh sản phẩm ( get product image )
async def get_image_binary(item_id: str, db: Database) -> Tuple[bytes, str]:
#async def get_image_binary(item_id: str, db: Database) -> (bytes, str):
    """Lấy dữ liệu nhị phân và mimetype của ảnh."""
    image_doc = db[config.IMAGES_COLLECTION].find_one({"item_id": item_id})
    if not image_doc:
        return None, None

    image_binary = image_doc.get("image_bin")
    media_type = image_doc.get("image_mime", "image/jpeg")
    
    if not image_binary:
        return None, None
        
    return image_binary, media_type