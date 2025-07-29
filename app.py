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
from upload import *
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



# -------------------
# POST API to add profile
# -------------------

SESSION_FILE = "sessions.json"

def load_sessions():
    with open(SESSION_FILE, "r") as f:
        return json.load(f)

def is_session_valid(session_id: str):
    sessions = load_sessions()
    for session in sessions["sessions"]:
        if session["session_id"] == session_id:
            return datetime.utcnow() < datetime.fromisoformat(session["expires_at"])
    return False

@app.get("/api/session-info")
def session_info(session_id: str):
    sessions = load_json("sessions.json")
    for session in sessions["sessions"]:
        if session["session_id"] == session_id:
            if datetime.utcnow() < datetime.fromisoformat(session["expires_at"]):
                return {"status": "success", "username": session["username"]}
            break
    return {"status": "error", "detail": "Session invalid or expired"}




@app.post("/api/add/sundarikanya", status_code=201)
async def add_sundari_entry(
    session_id: str = Form(...),
    uploader: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    tag: str = Form(...),
    category: str = Form(...),
    thumbnail: UploadFile = File(...),
    video: List[UploadFile] = File(...)  # Accept multiple files here
):
    if not is_session_valid(session_id):
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    os.makedirs("temp", exist_ok=True)

    # Save thumbnail
    thumb_path = f"temp/thumb_{datetime.now().timestamp()}.jpg"
    with open(thumb_path, "wb") as f:
        f.write(await thumbnail.read())
    raw_thumbnail = upload_image(thumb_path)

    # Save and upload each video
    video_links = []
    for vid_file in video:
        vid_path = f"temp/video_{datetime.now().timestamp()}_{vid_file.filename}"
        with open(vid_path, "wb") as f:
            f.write(await vid_file.read())
        uploaded_link = upload_to_root(vid_path)
        video_links.append(uploaded_link)

    # Generate new ID
    store = load_data()
    existing = store.get("data", {}).get("data", [])
    existing_ids = [int(item["id"]) for item in existing if "id" in item and item["id"].isdigit()]
    new_id_number = max(existing_ids, default=0) + 1
    new_id = f"{new_id_number:03d}"

    # Create entry
    entry = {
        "id": new_id,
        "uploader": uploader,
        "title": title,
        "description": description,
        "thumbnail": raw_thumbnail,
        "videourl": video_links,  # Save multiple video URLs
        "tag": [t.strip() for t in tag.split(",") if t.strip()],
        "category": [c.strip() for c in category.split(",") if c.strip()]
    }

    existing.append(entry)
    store["data"]["data"] = existing
    save_data(store)

    return {"status": "success", "added": 1}
    

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



@app.delete("/api/get/delete")
async def delete_video(id: str = Query(...), session_id: str = Query(...)):
    if not is_session_valid(session_id):
        raise HTTPException(status_code=401, detail="Invalid session")

    data = load_data()
    videos = data.get("data", {}).get("data", [])
    index_to_delete = next((i for i, v in enumerate(videos) if v["id"] == id), None)

    if index_to_delete is None:
        raise HTTPException(status_code=404, detail="Video not found")

    videos.pop(index_to_delete)
    data["data"]["data"] = videos
    save_data(data)

    return {"status": "success", "message": f"Video with id {id} deleted"}

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


@app.post("/api/get/update")
async def update_video(
    id: str = Form(...),
    session_id: str = Form(...),
    uploader: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    tag: str = Form(...),
    category: str = Form(...),
    thumbnail: Optional[UploadFile] = File(None),
    video: Optional[List[UploadFile]] = File(None)
):
    if not is_session_valid(session_id):
        raise HTTPException(status_code=401, detail="Invalid session")

    data = load_data()
    videos = data.get("data", {}).get("data", [])
    video_obj = next((v for v in videos if v["id"] == id), None)

    if not video_obj:
        raise HTTPException(status_code=404, detail="Video not found")

    video_obj["uploader"] = uploader
    video_obj["title"] = title
    video_obj["description"] = description
    video_obj["tag"] = [t.strip() for t in tag.split(",") if t.strip()]
    video_obj["category"] = [c.strip() for c in category.split(",") if c.strip()]

    if thumbnail:
        temp_thumb = f"temp/thumb_{datetime.now().timestamp()}.jpg"
        with open(temp_thumb, "wb") as f:
            f.write(await thumbnail.read())
        video_obj["thumbnail"] = upload_image(temp_thumb)

    if video:
        video_urls = []
        for vfile in video:
            temp_vid = f"temp/video_{datetime.now().timestamp()}_{vfile.filename}"
            with open(temp_vid, "wb") as f:
                f.write(await vfile.read())
            video_urls.append(upload_to_root(temp_vid))
        video_obj["videourl"] = video_urls

    save_data(data)

    return {"status": "success", "message": "Video updated"}


@app.post("/api/create-account")
def create_account(user: UserCreate):
    data = load_json(ACCOUNTS_FILE)
    if any(u["username"] == user.username for u in data["users"]):
        return {"status": "error", "detail": "Username already exists"}
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    data["users"].append({"username": user.username, "password": hashed})
    save_json(ACCOUNTS_FILE, data)
    return {"status": "success", "username": user.username}




SESSION_FILE = "sessions.json"

# Load/Save session functions
def load_sessions():
    if not os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "w") as f:
            json.dump({"sessions": []}, f)
    with open(SESSION_FILE, "r") as f:
        return json.load(f)

def save_sessions(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.post("/api/login")
def login(user: UserCreate):
    accounts = load_accounts()
    for account in accounts["users"]:
        if account["username"] == user.username:
            if bcrypt.checkpw(user.password.encode("utf-8"), account["password"].encode("utf-8")):
                # Generate session
                session_id = str(uuid.uuid4())
                expiry_time = (datetime.utcnow() + timedelta(days=7)).isoformat()

                # Store session
                sessions = load_sessions()
                sessions["sessions"].append({
                    "username": user.username,
                    "session_id": session_id,
                    "expires_at": expiry_time
                })
                save_sessions(sessions)

                return {
                    "status": "success",
                    "message": "Login successful",
                    "session_id": session_id,
                    "expires_at": expiry_time
                }

            else:
                raise HTTPException(status_code=401, detail="Incorrect password")

    raise HTTPException(status_code=404, detail="User not found")

@app.get("/api/check-session")
def check_session(session_id: str):
    sessions = load_sessions()
    for session in sessions["sessions"]:
        if session["session_id"] == session_id:
            if datetime.utcnow() < datetime.fromisoformat(session["expires_at"]):
                return {"status": "valid", "username": session["username"]}
            else:
                return {"status": "expired"}
    return {"status": "invalid"}
