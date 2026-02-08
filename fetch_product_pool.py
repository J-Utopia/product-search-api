import requests

# =====================
# API 기본 정보
# =====================
SEARCH_URL = "https://b2c-api.modetour.com/Package/SearchProductMaster"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "origin": "https://www.modetour.com",
    "referer": "https://www.modetour.com/",
    "user-agent": "Mozilla/5.0",
}

# =====================
# payload 생성 함수 (공통)
# =====================
def build_payload(areaKeyWordId, searchFrom, searchTo, startingPoint, travelType, page=1, pageSize=20):
    return {
        "themeId": "",
        "areaId": "",                    # ❗ 비워두거나 제거
        "areaKeyWordId": [areaKeyWordId],# ✅ UUID 기준
        "masterCodeIds": [],
        "masterCodes": [],
        "page": page,
        "pageSize": pageSize,
        "deviceType": "DVTPC",
        "searchFrom": searchFrom,
        "searchTo": searchTo,
        "sort": "Recommend",
        "isViewAllAvailableSeat": True,
        "travelType": "GNBOverseasTravel",
        "filter": {
            "typeFilter": "PGTOverseasTravel",
            "minPrice": 0,
            "maxPrice": 0,
            "startingPoint": startingPoint,
            "travelType": travelType,
        },
    }

def format_dates(dates):
    if not dates:
        return None
    return ", ".join(
        f'{d["night"]}박{d["days"]}일'
        for d in dates
        if isinstance(d, dict) and "night" in d and "days" in d
    )

def format_air_names(product_codes):
    if not product_codes:
        return None
    air_names = {
        pc.get("marketingAirName")
        for pc in product_codes
        if isinstance(pc, dict) and pc.get("marketingAirName")
    }
    return ", ".join(sorted(air_names)) if air_names else None

def fetch_product_pool(areaKeyWordId, searchFrom, searchTo, startingPoint, travelType, page=1, pageSize=20):
    """
    FastAPI에서 호출할 함수.
    return: dict (총상품/총페이지/상품리스트)
    """
    payload = build_payload(
        areaKeyWordId=areaKeyWordId,
        searchFrom=searchFrom,
        searchTo=searchTo,
        startingPoint=startingPoint,
        travelType=travelType,
        page=page,
        pageSize=pageSize,
    )

    res = requests.post(SEARCH_URL, headers=HEADERS, json=payload, timeout=20)
    res.raise_for_status()

    data = res.json()
    result = data.get("result", {}) or {}

    products = result.get("productMaster", []) or []
    output = []
    for p in products:
        master_code_id = p.get("masterCodeId")
        output.append(
            {
                "masterCode": p.get("masterCode"),
                "masterCodeId": master_code_id,
                "URL": f"https://www.modetour.com/product-common/{master_code_id}?type=group",
                "masterProductName": p.get("masterProductName"),
                "descriptions": p.get("descriptions"),
                "tags": p.get("tags"),
                "price": p.get("price"),
                "dates": format_dates(p.get("dates", [])),
                "airNames": format_air_names(p.get("productCodes", [])),
            }
        )

    return {
        "totalItems": result.get("totalItems"),
        "totalPages": result.get("totalPages"),
        "products": output,
    }
