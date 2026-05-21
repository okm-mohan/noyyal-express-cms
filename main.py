from fastapi import FastAPI
from fastapi import Request
from fastapi import Form
from fastapi import UploadFile
from fastapi import File

from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from typing import List

import shutil
import os
import pymysql

from slugify import slugify

# FASTAPI APP

app = FastAPI()

# STATIC FILES

app.mount("/static", StaticFiles(directory="static"), name="static")

# TEMPLATE DIRECTORY

templates = Jinja2Templates(directory="templates")

# CREATE UPLOAD FOLDER

if not os.path.exists("static/uploads"):

    os.makedirs("static/uploads")

# HOME PAGE

@app.get("/")
def home():

    return {

        "message": "Noyyal Express Backend Running"

    }

# ADMIN LOGIN PAGE

@app.get("/admin", response_class=HTMLResponse)
def admin_login(request: Request):

    return templates.TemplateResponse(

        request=request,
        name="admin/login.html"

    )

# ADMIN LOGIN POST

@app.post("/admin/login")
def admin_login_post(

    username: str = Form(...),
    password: str = Form(...)

):

    connection = pymysql.connect(

        host="localhost",
        user="root",
        password="",
        database="noyyalexpress"

    )

    cursor = connection.cursor()

    query = """

    SELECT * FROM user

    WHERE u_name=%s AND p_name=%s

    """

    cursor.execute(

        query,

        (

            username,
            password

        )

    )

    admin = cursor.fetchone()

    connection.close()

    if admin:

        return RedirectResponse(

            url="/dashboard",
            status_code=303

        )

    return {

        "message": "Invalid Username or Password"

    }

# DASHBOARD

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    return templates.TemplateResponse(

        request=request,
        name="admin/dashboard.html"

    )

# ADD NEWS PAGE

@app.get("/add-news", response_class=HTMLResponse)
def add_news_page(request: Request):

    connection = pymysql.connect(

        host="localhost",
        user="root",
        password="",
        database="noyyalexpress"

    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # GET CATEGORIES

    cursor.execute(

        "SELECT * FROM category WHERE status=1 ORDER BY category_name ASC"

    )

    categories = cursor.fetchall()

    connection.close()

    return templates.TemplateResponse(

        request=request,

        name="admin/add_news.html",

        context={

            "categories": categories

        }

    )

# SAVE NEWS

@app.post("/save-news")
async def save_news(

    category_id: int = Form(...),

    channel_id: int = Form(...),

    title: str = Form(...),

    description: str = Form(...),

    source: str = Form(None),

    video_link: str = Form(None),

    video_type: str = Form(None),

    is_breaking: str = Form(None),

    is_public: str = Form(None),

    send_notification: str = Form(None),

    images: List[UploadFile] = File([])

):

    # CREATE SLUG

    slug = slugify(title)

    # CHECKBOX VALUES

    breaking_value = 1 if is_breaking else 0

    public_value = 1 if is_public else 0

    notify_value = 1 if send_notification else 0

    # MYSQL CONNECTION

    connection = pymysql.connect(

        host="localhost",
        user="root",
        password="",
        database="noyyalexpress"

    )

    cursor = connection.cursor()

    # INSERT NEWS

    sql = """

    INSERT INTO news(

        category_id,
        channel_id,
        title,
        slug,
        description,
        source,
        video_link,
        link_type,
        is_breaking,
        is_public,
        notify,
        status

    )

    VALUES(

        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s

    )

    """

    values = (

        category_id,
        channel_id,
        title,
        slug,
        description,
        source,
        video_link,
        video_type,
        breaking_value,
        public_value,
        notify_value,
        1

    )

    cursor.execute(sql, values)

    connection.commit()

    # LAST INSERT ID

    news_id = cursor.lastrowid

    # SAVE IMAGES

    for image in images:

        if image.filename != "":

            filename = image.filename

            filepath = f"static/uploads/{filename}"

            with open(filepath, "wb") as buffer:

                shutil.copyfileobj(image.file, buffer)

            # INSERT IMAGE RECORD

            img_sql = """

            INSERT INTO news_images(

                news_id,
                image_name

            )

            VALUES(%s,%s)

            """

            cursor.execute(

                img_sql,

                (

                    news_id,
                    filename

                )

            )

    connection.commit()

    connection.close()

    return RedirectResponse(

        url="/news-list",

        status_code=303

    )

# NEWS LIST PAGE

@app.get("/news-list", response_class=HTMLResponse)
def news_list(

    request: Request,

    page: int = 1

):

    limit = 10

    offset = (page - 1) * limit

    # MYSQL CONNECTION

    connection = pymysql.connect(

        host="localhost",
        user="root",
        password="",
        database="noyyalexpress"

    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # TOTAL NEWS COUNT

    cursor.execute(

        "SELECT COUNT(*) as total FROM news"

    )

    total_news = cursor.fetchone()['total']

    total_pages = (total_news + limit - 1) // limit

    # GET NEWS

    query = """

    SELECT

        news.*,

        category.category_name,

        news_images.image_name

    FROM news

    LEFT JOIN category

    ON news.category_id = category.id

    LEFT JOIN news_images

    ON news.id = news_images.news_id

    GROUP BY news.id

    ORDER BY news.id DESC

    LIMIT %s OFFSET %s

    """

    cursor.execute(

        query,

        (

            limit,
            offset

        )

    )

    news_list = cursor.fetchall()

    # GET CATEGORY LIST

    cursor.execute(

        "SELECT * FROM category WHERE status=1 ORDER BY category_name ASC"

    )

    categories = cursor.fetchall()

    connection.close()

    return templates.TemplateResponse(

        request=request,

        name="admin/news_list.html",

        context={

            "news_list": news_list,

            "categories": categories,

            "page": page,

            "total_pages": total_pages,

            "total_news": total_news

        }

    )