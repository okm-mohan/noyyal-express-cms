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

# NEWS LIST PAGE WITH SEARCH + CATEGORY FILTER

@app.get("/news-list", response_class=HTMLResponse)
def news_list(

    request: Request,

    page: int = 1,

    search: str = "",

    category_id: str = ""

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

    # CONDITIONS

    conditions = []

    values = []

    # SEARCH FILTER

    if search != "":

        conditions.append("""

            (

                news.title LIKE %s

                OR news.description LIKE %s

                OR category.category_name LIKE %s

            )

        """)

        keyword = "%" + search + "%"

        values.extend([

            keyword,
            keyword,
            keyword

        ])

    # CATEGORY FILTER

    if category_id != "":

        conditions.append(

            "news.category_id = %s"

        )

        values.append(category_id)

    # FINAL WHERE CLAUSE

    where_clause = ""

    if conditions:

        where_clause = "WHERE " + " AND ".join(conditions)

    # TOTAL COUNT

    count_query = f"""

    SELECT COUNT(DISTINCT news.id) as total

    FROM news

    LEFT JOIN category

    ON news.category_id = category.id

    {where_clause}

    """

    cursor.execute(

        count_query,

        values

    )

    total_news = cursor.fetchone()['total']

    total_pages = (total_news + limit - 1) // limit

    # NEWS QUERY

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

    LIMIT %s OFFSET %s

    """

    final_values = values + [limit, offset]

    cursor.execute(

        query,

        final_values

    )

    news_list = cursor.fetchall()

    # CATEGORY LIST

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

            "total_news": total_news,

            "search": search,

            "selected_category_id": int(category_id) if category_id else ""

        }

    )

# EDIT NEWS PAGE

@app.get("/edit-news/{news_id}", response_class=HTMLResponse)
def edit_news_page(

    request: Request,

    news_id: int

):

    connection = pymysql.connect(

        host="localhost",
        user="root",
        password="",
        database="noyyalexpress"

    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # GET NEWS

    cursor.execute(

        "SELECT * FROM news WHERE id=%s",

        (news_id,)

    )

    news = cursor.fetchone()

    # GET CATEGORIES

    cursor.execute(

        "SELECT * FROM category WHERE status=1 ORDER BY category_name ASC"

    )

    categories = cursor.fetchall()

    # GET IMAGE

    cursor.execute(

        "SELECT * FROM news_images WHERE news_id=%s LIMIT 1",

        (news_id,)

    )

    image = cursor.fetchone()

    connection.close()

    return templates.TemplateResponse(

        request=request,

        name="admin/edit_news.html",

        context={

            "news": news,
            "categories": categories,
            "image": image

        }

    )

# UPDATE NEWS

@app.post("/update-news/{news_id}")
async def update_news(

    news_id: int,

    category_id: int = Form(...),

    title: str = Form(...),

    description: str = Form(...),

    source: str = Form(None),

    is_breaking: str = Form(None),

    image: UploadFile = File(None)

):

    slug = slugify(title)

    breaking_value = 1 if is_breaking else 0

    connection = pymysql.connect(

        host="localhost",
        user="root",
        password="",
        database="noyyalexpress"

    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # UPDATE NEWS

    sql = """

    UPDATE news

    SET

        category_id=%s,
        title=%s,
        slug=%s,
        description=%s,
        source=%s,
        is_breaking=%s

    WHERE id=%s

    """

    values = (

        category_id,
        title,
        slug,
        description,
        source,
        breaking_value,
        news_id

    )

    cursor.execute(sql, values)

    # UPDATE IMAGE

    if image and image.filename != "":

        cursor.execute(

            "SELECT * FROM news_images WHERE news_id=%s LIMIT 1",

            (news_id,)

        )

        old_image = cursor.fetchone()

        if old_image:

            old_path = f"static/uploads/{old_image['image_name']}"

            if os.path.exists(old_path):

                os.remove(old_path)

            cursor.execute(

                "DELETE FROM news_images WHERE news_id=%s",

                (news_id,)

            )

        filename = image.filename

        filepath = f"static/uploads/{filename}"

        with open(filepath, "wb") as buffer:

            shutil.copyfileobj(image.file, buffer)

        cursor.execute(

            """

            INSERT INTO news_images(

                news_id,
                image_name

            )

            VALUES(%s,%s)

            """,

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

# DELETE NEWS

@app.get("/delete-news/{news_id}")
def delete_news(news_id: int):

    connection = pymysql.connect(

        host="localhost",
        user="root",
        password="",
        database="noyyalexpress"

    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # GET IMAGES

    cursor.execute(

        "SELECT * FROM news_images WHERE news_id=%s",

        (news_id,)

    )

    images = cursor.fetchall()

    # DELETE IMAGE FILES

    for image in images:

        image_path = f"static/uploads/{image['image_name']}"

        if os.path.exists(image_path):

            os.remove(image_path)

    # DELETE IMAGE RECORDS

    cursor.execute(

        "DELETE FROM news_images WHERE news_id=%s",

        (news_id,)

    )

    # DELETE NEWS

    cursor.execute(

        "DELETE FROM news WHERE id=%s",

        (news_id,)

    )

    connection.commit()

    connection.close()

    return RedirectResponse(

        url="/news-list",

        status_code=303

    )