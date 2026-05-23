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

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI()

# ============================================
# STATIC FILES
# ============================================

app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================
# TEMPLATE DIRECTORY
# ============================================

templates = Jinja2Templates(directory="templates")

# ============================================
# CREATE UPLOAD FOLDER
# ============================================

if not os.path.exists("static/uploads"):

    os.makedirs("static/uploads")

# ============================================
# DATABASE CONNECTION
# ============================================

def get_connection():

    connection = pymysql.connect(

        host="localhost",
        user="root",
        password="",
        database="noyyalexpress"

    )

    return connection

# ============================================
# FRONTEND HOME PAGE
# ============================================

@app.get("/", response_class=HTMLResponse)
def frontend_home(

    request: Request,

    search: str = ""

):

    connection = get_connection()

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # ============================================
    # MENU CATEGORIES
    # ============================================

    cursor.execute(

        """

        SELECT *

        FROM category

        WHERE status=1
        AND menu_order > 0

        ORDER BY menu_order ASC

        LIMIT 8

        """

    )

    menu_categories = cursor.fetchall()

    # ============================================
    # MORE MENU CATEGORIES
    # ============================================

    cursor.execute(

        """

        SELECT *

        FROM category

        WHERE status=1
        AND menu_order = 0

        ORDER BY category_name ASC

        """

    )

    more_categories = cursor.fetchall()

    # ============================================
    # HERO NEWS
    # ============================================

    cursor.execute(

        """

        SELECT

            news.*,
            news_images.image_name

        FROM news

        LEFT JOIN news_images

        ON news.id = news_images.news_id

        GROUP BY news.id

        ORDER BY news.id DESC

        LIMIT 5

        """

    )

    hero_news = cursor.fetchall()

    # ============================================
    # BREAKING NEWS
    # ============================================

    cursor.execute(

        """

        SELECT *

        FROM news

        WHERE is_breaking=1

        ORDER BY id DESC

        LIMIT 10

        """

    )

    breaking_news = cursor.fetchall()

    # ============================================
    # SEARCH CONDITION
    # ============================================

    where_clause = ""

    values = []

    if search != "":

        where_clause = """

        WHERE

            news.title LIKE %s

            OR news.description LIKE %s

            OR category.category_name LIKE %s

        """

        keyword = "%" + search + "%"

        values = [

            keyword,
            keyword,
            keyword

        ]

    # ============================================
    # LATEST NEWS
    # ============================================

    query = f"""

    SELECT

        news.*,
        category.category_name,
        news_images.image_name

    FROM news

    LEFT JOIN category

    ON news.category_id = category.id

    LEFT JOIN news_images

    ON news.id = news_images.news_id

    {where_clause}

    GROUP BY news.id

    ORDER BY news.id DESC

    LIMIT 20

    """

    cursor.execute(query, values)

    latest_news = cursor.fetchall()

    connection.close()

    return templates.TemplateResponse(

        request=request,

        name="frontend/index.html",

        context={

            "menu_categories": menu_categories,
            "more_categories": more_categories,
            "hero_news": hero_news,
            "breaking_news": breaking_news,
            "latest_news": latest_news,
            "search": search

        }

    )

# ============================================
# NEWS DETAIL PAGE
# ============================================

@app.get("/news/{news_id}/{slug:path}", response_class=HTMLResponse)
def news_detail(

    request: Request,

    news_id: int,

    slug: str

):

    connection = get_connection()

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # ============================================
    # MENU CATEGORIES
    # ============================================

    cursor.execute(

        """

        SELECT *

        FROM category

        WHERE status=1
        AND menu_order > 0

        ORDER BY menu_order ASC

        LIMIT 8

        """

    )

    menu_categories = cursor.fetchall()

    # ============================================
    # MORE MENU CATEGORIES
    # ============================================

    cursor.execute(

        """

        SELECT *

        FROM category

        WHERE status=1
        AND menu_order = 0

        ORDER BY category_name ASC

        """

    )

    more_categories = cursor.fetchall()

    # ============================================
    # SINGLE NEWS
    # ============================================

    cursor.execute(

        """

        SELECT

            news.*,
            category.category_name,
            news_images.image_name

        FROM news

        LEFT JOIN category

        ON news.category_id = category.id

        LEFT JOIN news_images

        ON news.id = news_images.news_id

        WHERE news.id=%s

        GROUP BY news.id

        LIMIT 1

        """,

        (news_id,)

    )

    news = cursor.fetchone()

    if not news:

        return HTMLResponse(

            content="<h1>News Not Found</h1>",

            status_code=404

        )

    # ============================================
    # RELATED NEWS
    # ============================================

    cursor.execute(

        """

        SELECT

            news.*,
            news_images.image_name

        FROM news

        LEFT JOIN news_images

        ON news.id = news_images.news_id

        WHERE news.category_id=%s

        AND news.id!=%s

        GROUP BY news.id

        ORDER BY news.id DESC

        LIMIT 6

        """,

        (

            news['category_id'],
            news_id

        )

    )

    related_news = cursor.fetchall()

    # ============================================
    # TRENDING NEWS
    # ============================================

    cursor.execute(

        """

        SELECT

            news.*,
            news_images.image_name

        FROM news

        LEFT JOIN news_images

        ON news.id = news_images.news_id

        GROUP BY news.id

        ORDER BY news.id DESC

        LIMIT 5

        """

    )

    trending_news = cursor.fetchall()

    connection.close()

    return templates.TemplateResponse(

        request=request,

        name="frontend/news_detail.html",

        context={

            "menu_categories": menu_categories,
            "more_categories": more_categories,
            "news": news,
            "related_news": related_news,
            "trending_news": trending_news

        }

    )

# ============================================
# CATEGORY NEWS PAGE
# ============================================

@app.get("/category/{category_id}/{slug:path}", response_class=HTMLResponse)
def category_news(

    request: Request,

    category_id: int,

    slug: str

):

    connection = get_connection()

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # ============================================
    # MENU CATEGORIES
    # ============================================

    cursor.execute(

        """

        SELECT *

        FROM category

        WHERE status=1
        AND menu_order > 0

        ORDER BY menu_order ASC

        LIMIT 8

        """

    )

    menu_categories = cursor.fetchall()

    # ============================================
    # MORE MENU CATEGORIES
    # ============================================

    cursor.execute(

        """

        SELECT *

        FROM category

        WHERE status=1
        AND menu_order = 0

        ORDER BY category_name ASC

        """

    )

    more_categories = cursor.fetchall()

    # ============================================
    # CURRENT CATEGORY
    # ============================================

    cursor.execute(

        """

        SELECT *

        FROM category

        WHERE id=%s

        LIMIT 1

        """,

        (category_id,)

    )

    current_category = cursor.fetchone()

    # ============================================
    # CATEGORY NEWS
    # ============================================

    cursor.execute(

        """

        SELECT

            news.*,
            news_images.image_name

        FROM news

        LEFT JOIN news_images

        ON news.id = news_images.news_id

        WHERE news.category_id=%s

        GROUP BY news.id

        ORDER BY news.id DESC

        LIMIT 50

        """,

        (category_id,)

    )

    category_news = cursor.fetchall()

    # ============================================
    # TRENDING NEWS
    # ============================================

    cursor.execute(

        """

        SELECT

            news.*,
            news_images.image_name

        FROM news

        LEFT JOIN news_images

        ON news.id = news_images.news_id

        GROUP BY news.id

        ORDER BY news.id DESC

        LIMIT 5

        """

    )

    trending_news = cursor.fetchall()

    connection.close()

    return templates.TemplateResponse(

        request=request,

        name="frontend/category_news.html",

        context={

            "menu_categories": menu_categories,
            "more_categories": more_categories,
            "current_category": current_category,
            "category_news": category_news,
            "trending_news": trending_news

        }

    )

# ============================================
# ADMIN LOGIN PAGE
# ============================================

@app.get("/admin", response_class=HTMLResponse)
def admin_login(request: Request):

    return templates.TemplateResponse(

        request=request,
        name="admin/login.html"

    )

# ============================================
# ADMIN LOGIN POST
# ============================================

@app.post("/admin/login")
def admin_login_post(

    username: str = Form(...),
    password: str = Form(...)

):

    connection = get_connection()

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

# ============================================
# DASHBOARD
# ============================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    return templates.TemplateResponse(

        request=request,
        name="admin/dashboard.html"

    )

# ============================================
# ADD NEWS PAGE
# ============================================

@app.get("/add-news", response_class=HTMLResponse)
def add_news_page(request: Request):

    connection = get_connection()

    cursor = connection.cursor(pymysql.cursors.DictCursor)

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

# ============================================
# SAVE NEWS
# ============================================

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

    slug = slugify(title)

    if slug == "":

        slug = "news"

    breaking_value = 1 if is_breaking else 0

    public_value = 1 if is_public else 0

    notify_value = 1 if send_notification else 0

    connection = get_connection()

    cursor = connection.cursor()

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

    news_id = cursor.lastrowid

    # ============================================
    # SAVE IMAGES
    # ============================================

    for image in images:

        if image.filename != "":

            filename = image.filename

            filepath = f"static/uploads/{filename}"

            with open(filepath, "wb") as buffer:

                shutil.copyfileobj(image.file, buffer)

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