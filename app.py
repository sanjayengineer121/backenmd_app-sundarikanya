from fastapi import FastAPI, Request, Form, status, HTTPException,File, UploadFile,Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse,FileResponse
from fastapi.templating import Jinja2Templates
import json
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
import os,shutil
import uuid
from fastapi.middleware.cors import CORSMiddleware
import bcrypt
from typing import Union
import os
from datetime import datetime, timedelta
import uuid

app = FastAPI()

# Set up templates folder
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




class UpdateVideo(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    videourl: Optional[List[str]] = None
    tag: Optional[List[str]] = None
    category: Optional[List[str]] = None


DATA_FILE = "data.json"

ACCOUNTS_FILE = "accounts.json"

# Create the JSON file if it doesn't exist
if not os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump({"users": []}, f)

class UserCreate(BaseModel):
    username:str
    password:str

def load_accounts():
    with open(ACCOUNTS_FILE,'r') as f:
        return json.load(f)


def save_accounts(data):
    with open(ACCOUNTS_FILE,'w') as f:
        json.dump(data,f,indent=2)



class VideoEntry(BaseModel):
    title: str
    description: str
    thumbnail: str
    videourl: List[str]  # ✅ now expecting a list always
    tag: List[str]
    category: List[str]

class UploadData(BaseModel):
    uploader: str
    session_id: str
    videos: List[VideoEntry]

# -------------------
# File helpers
# -------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"data": {"data": []}}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"data": {"data": []}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)



ENGAGEMENT_FILE = "engagement.json"

# Initialize file if it doesn't exist
if not os.path.exists(ENGAGEMENT_FILE):
    with open(ENGAGEMENT_FILE, "w") as f:
        json.dump({}, f)

def load_engagement():
    with open(ENGAGEMENT_FILE, "r") as f:
        return json.load(f)

def save_engagement(data):
    with open(ENGAGEMENT_FILE, "w") as f:
        json.dump(data, f, indent=2)



def initialize_video(video_id):
    data = load_engagement()
    if video_id not in data:
        data[video_id] = {"likes": 0, "views": 0, "shares": 0}
        save_engagement(data)
    return data

@app.get("/api/get/video")
def get_video(video_id: str = Query(..., alias="id")):
    data = initialize_video(video_id)
    data[video_id]["views"] += 1
    save_engagement(data)
    return {"status": "success", "video_id": video_id, "counts": data[video_id]}

@app.post("/api/like")
def add_like(video_id: str = Query(..., alias="id")):
    data = initialize_video(video_id)
    data[video_id]["likes"] += 1
    save_engagement(data)
    return {"status": "success", "video_id": video_id, "likes": data[video_id]["likes"]}

@app.post("/api/share")
def add_share(video_id: str = Query(..., alias="id")):
    data = initialize_video(video_id)
    data[video_id]["shares"] += 1
    save_engagement(data)
    return {"status": "success", "video_id": video_id, "shares": data[video_id]["shares"]}

@app.get("/api/get/stats")
def get_stats(video_id: str = Query(..., alias="id")):
    data = initialize_video(video_id)
    return {"status": "success", "video_id": video_id, "counts": data[video_id]}


# Utils
def load_json(file): return json.load(open(file))
def save_json(file, data): json.dump(data, open(file, "w"), indent=2)

# ROUTES
@app.get("/", response_class=HTMLResponse)
def show_create_account(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/home", response_class=HTMLResponse)
def serve_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/update")
async def update_page(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})




@app.get("/api/get/sundarikanya")
def get_video_by_id(
    id: Optional[str] = Query(None),
    page: int = Query(1, ge=1)
):
    data = load_data()["data"]["data"]
    total = len(data)
    
    # ✅ Return specific video by ID
    if id:
        formatted_id = id.zfill(3)
        result = next((item for item in data if item["id"] == formatted_id), None)
        if not result:
            raise HTTPException(status_code=404, detail=f"Video with ID {formatted_id} not found.")
        return result

    # ✅ Pagination logic from end
    per_page = 40
    start = max(total - (page * per_page), 0)
    end = total - ((page - 1) * per_page)
    paginated_data = data[start:end]

    return {
        "status": "success",
        "total": total,
        "page": page,
        "per_page": per_page,
        "data": list(reversed(paginated_data))  # So newest is always first
    }


# Utility: Convert ["Pakistani,Teen,,Model"] → ["Pakistani", "Teen", "Model"]
def clean_split_list(value):
    if isinstance(value, list):
        cleaned = []
        for v in value:
            cleaned.extend([x.strip() for x in v.split(",") if x.strip()])
        return cleaned
    return []

@app.get("/api/get/sundarikanya1")
def get_sundari_entries(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = 1,
    limit: int = 36
):
    store = load_data()  # Load your JSON DB or file
    all_entries = store.get("data", {}).get("data", [])

    filtered_entries = []

    for entry in all_entries:
        cat_list = clean_split_list(entry.get("category", []))
        tag_list = clean_split_list(entry.get("tag", []))

        match_category = True
        match_tag = True

        if category:
            match_category = any(c.lower() == category.lower() for c in cat_list)

        if tag:
            match_tag = any(t.lower() == tag.lower() for t in tag_list)

        if match_category and match_tag:
            filtered_entries.append(entry)

    total = len(filtered_entries)

    # Pagination logic
    start = (page - 1) * limit
    end = start + limit
    paginated_data = filtered_entries[start:end]

    return {
        "status": "success",
        "filter": {"category": category, "tag": tag},
        "page": page,
        "limit": limit,
        "total": total,
        "data": paginated_data
    }



@app.get("/api/get/search")
def search_sundari_entries(
    query: str = Query(..., description="Search by keyword in title, description, tag, or category"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(36, ge=1, le=100, description="Number of items per page"),
):
    data_store = load_data()
    all_entries = data_store.get("data", {}).get("data", [])

    query_lower = query.lower()
    filtered_results = []

    for entry in all_entries:
        title_match = query_lower in entry.get("title", "").lower()
        description_match = query_lower in entry.get("description", "").lower()
        tag_match = any(query_lower in tag.lower() for tag in entry.get("tag", []))
        category_match = any(query_lower in cat.lower() for cat in entry.get("category", []))

        if title_match or description_match or tag_match or category_match:
            filtered_results.append(entry)

    # Pagination calculation
    total = len(filtered_results)
    start = (page - 1) * limit
    end = start + limit
    paginated_results = filtered_results[start:end]

    return {
        "status": "success",
        "query": query,
        "page": page,
        "limit": limit,
        "total_results": total,
        "data": paginated_results
    }



@app.get("/api/get/bestcategory")
def get_best_category():
    data_store = load_data()
    all_entries = data_store.get("data", {}).get("data", [])

    category_counter = {}

    for entry in all_entries:
        categories = entry.get("category", [])
        for cat in categories:
            cat_clean = cat.strip().lower()
            if cat_clean:
                category_counter[cat_clean] = category_counter.get(cat_clean, 0) + 1

    # Sort categories by count descending
    sorted_categories = sorted(category_counter.items(), key=lambda x: x[1], reverse=True)

    best_categories = [{"category": cat, "count": count} for cat, count in sorted_categories]

    return {
        "status": "success",
        "total_categories": len(best_categories),
        "best_categories": best_categories
    }


