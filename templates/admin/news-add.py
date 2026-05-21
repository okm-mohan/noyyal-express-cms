from fastapi import FastAPI, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import json

from database import Base, engine, get_db
from models import News

Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ✅ NEWS ADD API (FULL PHP REPLACEMENT)
@app.post("/news/add")
async def add_news(
    category_id: int = Form(...),
    channel_id: Optional[int] = Form(None),
    title: str = Form(...),
    description: str = Form(...),
    source: Optional[str] = Form(None),
    video_link: Optional[str] = Form(None),
    video_link_type: Optional[str] = Form(None),
    is_public: Optional[bool] = Form(False),
    notify: Optional[bool] = Form(False),
    files: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):

    # 📸 Save uploaded images
    image_paths = []

    if files:
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            image_paths.append(file_path)

    # 🧠 Create DB record
    news = News(
        category_id=category_id,
        channel_id=channel_id,
        title=title,
        description=description,
        source=source,
        video_link=video_link,
        video_link_type=video_link_type,
        images=json.dumps(image_paths),
        is_public=is_public,
        notify=notify
    )

    db.add(news)
    db.commit()
    db.refresh(news)

    return {
        "status": "success",
        "message": "News added successfully",
        "news_id": news.id,
        "uploaded_images": image_paths
    }


# 📄 GET NEWS (for testing)
@app.get("/news")
def get_news(db: Session = Depends(get_db)):
    return db.query(News).all()