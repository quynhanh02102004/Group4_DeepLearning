# backend/models.py
from pydantic import BaseModel
from typing import List, Optional

# API Schemas 

class SearchHit(BaseModel):
    item_id: str
    score: float
    title: Optional[str] = None
    main_category: Optional[str] = None
    sub_category: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[SearchHit]