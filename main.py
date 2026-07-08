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

    configs = [
        {
            "host": os.getenv("DB_HOST", "localhost"),
            "user": os.getenv("DB_USER", "noyyalexpress_admin"),
            "password": os.getenv("DB_PASSWORD", "Epiclife@cbe32#"),
            "database": os.getenv("DB_NAME", "noyyalexpress")
        },
        {
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "noyyalexpress"
        }
    ]

    last_error = None

    for config in configs:

        try:

            return pymysql.connect(**config)

        except pymysql.MySQLError as error:

            last_error = error

    raise last_error

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
# SETTINGS PAGE
# ============================================

@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):

    connection = get_connection()

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # ============================================
    # GET SETTINGS
    # ============================================

    cursor.execute(

        """

        SELECT *

        FROM settings

        ORDER BY id DESC

        LIMIT 1

        """

    )

    settings = cursor.fetchone()

    connection.close()

    return templates.TemplateResponse(

        request=request,

        name="admin/settings.html",

        context={

            "settings": settings

        }

    )


# ============================================
# UPDATE SETTINGS
# ============================================

@app.post("/update-settings")
async def update_settings(

    website_name: str = Form(""),

    contact_email: str = Form(""),

    phone: str = Form(""),

    address: str = Form(""),

    meta_title: str = Form(""),

    meta_description: str = Form(""),

    facebook_url: str = Form(""),

    youtube_url: str = Form(""),

    instagram_url: str = Form(""),

    twitter_url: str = Form(""),

    footer_text: str = Form(""),

    logo: UploadFile = File(None),

    favicon: UploadFile = File(None)

):

    connection = get_connection()

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # ============================================
    # CHECK SETTINGS EXISTS
    # ============================================

    cursor.execute(

        """

        SELECT *

        FROM settings

        LIMIT 1

        """

    )

    existing_settings = cursor.fetchone()

    # ============================================
    # DEFAULT VALUES
    # ============================================

    logo_name = ""

    favicon_name = ""

    if existing_settings:

        logo_name = existing_settings["logo"]

        favicon_name = existing_settings["favicon"]

    # ============================================
    # SAVE LOGO
    # ============================================

    if logo and logo.filename != "":

        logo_name = logo.filename

        logo_path = f"static/uploads/{logo_name}"

        with open(logo_path, "wb") as buffer:

            shutil.copyfileobj(logo.file, buffer)

    # ============================================
    # SAVE FAVICON
    # ============================================

    if favicon and favicon.filename != "":

        favicon_name = favicon.filename

        favicon_path = f"static/uploads/{favicon_name}"

        with open(favicon_path, "wb") as buffer:

            shutil.copyfileobj(favicon.file, buffer)

    # ============================================
    # UPDATE SETTINGS
    # ============================================

    if existing_settings:

        cursor.execute(

            """

            UPDATE settings

            SET

                website_name=%s,
                contact_email=%s,
                phone=%s,
                address=%s,
                meta_title=%s,
                meta_description=%s,
                facebook_url=%s,
                youtube_url=%s,
                instagram_url=%s,
                twitter_url=%s,
                footer_text=%s,
                logo=%s,
                favicon=%s

            WHERE id=%s

            """,

            (

                website_name,
                contact_email,
                phone,
                address,
                meta_title,
                meta_description,
                facebook_url,
                youtube_url,
                instagram_url,
                twitter_url,
                footer_text,
                logo_name,
                favicon_name,
                existing_settings["id"]

            )

        )

    # ============================================
    # INSERT SETTINGS
    # ============================================

    else:

        cursor.execute(

            """

            INSERT INTO settings(

                website_name,
                contact_email,
                phone,
                address,
                meta_title,
                meta_description,
                facebook_url,
                youtube_url,
                instagram_url,
                twitter_url,
                footer_text,
                logo,
                favicon

            )

            VALUES(

                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s

            )

            """,

            (

                website_name,
                contact_email,
                phone,
                address,
                meta_title,
                meta_description,
                facebook_url,
                youtube_url,
                instagram_url,
                twitter_url,
                footer_text,
                logo_name,
                favicon_name

            )

        )

    connection.commit()

    connection.close()

    return RedirectResponse(

        url="/settings",

        status_code=303

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

# =========================================================
# NEWS LIST PAGE
# =========================================================

@app.get("/news-list", response_class=HTMLResponse)
def news_list(

    request: Request,

    page: int = 1,

    search: str = "",

    category_id: int = 0

):

    connection = get_connection()

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    limit = 10

    offset = (page - 1) * limit

    # ============================================
    # CATEGORY LIST
    # ============================================

    cursor.execute("""

        SELECT *

        FROM category

        WHERE status=1

        ORDER BY category_name ASC

    """)

    categories = cursor.fetchall()

    # ============================================
    # WHERE CONDITION
    # ============================================

    where_clause = " WHERE 1=1 "

    values = []

    # SEARCH

    if search != "":

        where_clause += """

        AND (

            news.title LIKE %s

            OR news.description LIKE %s

        )

        """

        keyword = "%" + search + "%"

        values.extend([keyword, keyword])

    # CATEGORY FILTER

    if category_id != 0:

        where_clause += """

        AND news.category_id=%s

        """

        values.append(category_id)

    # ============================================
    # TOTAL NEWS COUNT
    # ============================================

    count_query = f"""

    SELECT COUNT(*) as total

    FROM news

    {where_clause}

    """

    cursor.execute(count_query, values)

    total_news_result = cursor.fetchone()

    total_news = total_news_result["total"]

    total_pages = (total_news + limit - 1) // limit

    # ============================================
    # NEWS LIST
    # ============================================

    query = f"""

    SELECT

        news.*,
        category.category_name,
        MIN(news_images.image_name) as image_name

    FROM news

    LEFT JOIN category

    ON news.category_id = category.id

    LEFT JOIN news_images

    ON news.id = news_images.news_id

    {where_clause}

    GROUP BY news.id

    ORDER BY news.id DESC

    LIMIT %s OFFSET %s

    """

    final_values = values + [limit, offset]

    cursor.execute(query, final_values)

    news_list = cursor.fetchall()

    connection.close()

    # ============================================
    # RETURN TEMPLATE
    # ============================================

    return templates.TemplateResponse(

        request=request,

        name="admin/news_list.html",

        context={

            "news_list": news_list,
            "categories": categories,
            "selected_category_id": category_id,
            "search": search,
            "total_news": total_news,
            "page": page,
            "total_pages": total_pages

        }

    )


# ============================================
# EDIT NEWS PAGE
# ============================================

@app.get("/edit-news/{news_id}", response_class=HTMLResponse)
def edit_news_page(

    request: Request,

    news_id: int

):

    connection = get_connection()

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # ============================================
    # GET ALL CATEGORIES
    # ============================================

    cursor.execute(

        """

        SELECT *

        FROM category

        WHERE status=1

        ORDER BY category_name ASC

        """

    )

    categories = cursor.fetchall()

    # ============================================
    # GET SINGLE NEWS
    # ============================================

    cursor.execute(

        """

        SELECT *

        FROM news

        WHERE id=%s

        LIMIT 1

        """,

        (news_id,)

    )

    news = cursor.fetchone()

    connection.close()

    # NEWS NOT FOUND

    if not news:

        return HTMLResponse(

            content="<h1>News Not Found</h1>",

            status_code=404

        )

    # ============================================
    # LOAD EDIT PAGE
    # ============================================

    return templates.TemplateResponse(

        request=request,

        name="admin/edit_news.html",

        context={

            "news": news,
            "categories": categories

        }

    )


# ============================================
# UPDATE NEWS
# ============================================

@app.post("/update-news/{news_id}")
async def update_news(

    news_id: int,

    category_id: int = Form(0),

    channel_id: int = Form(0),

    title: str = Form(""),

    description: str = Form(""),

    source: str = Form(None),

    video_link: str = Form(None),

    video_type: str = Form(None),

    is_breaking: str = Form(None),

    is_public: str = Form(None),

    send_notification: str = Form(None)

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

    UPDATE news

    SET

        category_id=%s,
        channel_id=%s,
        title=%s,
        slug=%s,
        description=%s,
        source=%s,
        video_link=%s,
        link_type=%s,
        is_breaking=%s,
        is_public=%s,
        notify=%s

    WHERE id=%s

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
        news_id

    )

    cursor.execute(sql, values)

    connection.commit()

    connection.close()

    return RedirectResponse(

        url="/news-list",

        status_code=303

    )


# ============================================
# DELETE NEWS
# ============================================

@app.get("/delete-news/{news_id}")
def delete_news(news_id: int):

    connection = get_connection()

    cursor = connection.cursor()

    # ============================================
    # DELETE NEWS IMAGES FIRST
    # ============================================

    cursor.execute(

        """

        DELETE FROM news_images

        WHERE news_id=%s

        """,

        (news_id,)

    )

    # ============================================
    # DELETE NEWS
    # ============================================

    cursor.execute(

        """

        DELETE FROM news

        WHERE id=%s

        """,

        (news_id,)

    )

    connection.commit()

    connection.close()

    return RedirectResponse(

        url="/news-list",

        status_code=303

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


# ============================================
# ANALYTICS PAGE
# ============================================

@app.get("/analytics", response_class=HTMLResponse)
def analytics_page(request: Request):

    connection = get_connection()

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # TOTAL NEWS

    cursor.execute(

        """

        SELECT COUNT(*) as total_news

        FROM news

        """

    )

    total_news = cursor.fetchone()["total_news"]

    # BREAKING NEWS

    cursor.execute(

        """

        SELECT COUNT(*) as breaking_news

        FROM news

        WHERE is_breaking=1

        """

    )

    breaking_news = cursor.fetchone()["breaking_news"]

    # TOTAL VIEWS

    cursor.execute(

        """

        SELECT SUM(tot_view) as total_views

        FROM news

        """

    )

    views_result = cursor.fetchone()

    total_views = views_result["total_views"] or 0

    # TOTAL CATEGORIES

    cursor.execute(

        """

        SELECT COUNT(*) as total_categories

        FROM category

        """

    )

    total_categories = cursor.fetchone()["total_categories"]

    # TOP VIEWED NEWS

    cursor.execute(

        """

        SELECT

            title,
            tot_view

        FROM news

        ORDER BY tot_view DESC

        LIMIT 5

        """

    )

    top_news = cursor.fetchall()

    connection.close()

    return templates.TemplateResponse(

        request=request,

        name="admin/analytics.html",

        context={

            "total_news": total_news,
            "breaking_news": breaking_news,
            "total_views": total_views,
            "total_categories": total_categories,
            "top_news": top_news

        }

    )
