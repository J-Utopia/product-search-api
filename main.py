from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from fetch_product_pool import fetch_product_pool

app = FastAPI(title="Product Search API")

# =====================
# 요청 Body 스키마
# =====================
class SearchRequest(BaseModel):
    areaId: int
    searchFrom: str
    searchTo: str
    startingPoint: List[str]
    travelType: List[str]
    page: int = 1
    pageSize: int = 20


# =====================
# 헬스체크
# =====================
@app.get("/")
def health_check():
    return {"status": "ok"}


# =====================
# 상품 검색 API
# =====================
@app.post("/search")
def search_products(req: SearchRequest):
    try:
        result = fetch_product_pool(
            areaId=req.areaId,
            searchFrom=req.searchFrom,
            searchTo=req.searchTo,
            startingPoint=req.startingPoint,
            travelType=req.travelType,
            page=req.page,
            pageSize=req.pageSize,
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
