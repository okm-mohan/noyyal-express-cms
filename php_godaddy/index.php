<?php
session_start();

$config = require __DIR__ . '/config.php';

function db()
{
    static $pdo = null;
    global $config;

    if ($pdo === null) {
        $dsn = "mysql:host={$config['db_host']};port={$config['db_port']};dbname={$config['db_name']};charset=utf8mb4";
        $pdo = new PDO($dsn, $config['db_user'], $config['db_pass'], [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ]);
    }

    return $pdo;
}

function h($value)
{
    return htmlspecialchars((string)$value, ENT_QUOTES, 'UTF-8');
}

function slugify($text)
{
    $text = strtolower(trim((string)$text));
    $text = preg_replace('/[^a-z0-9]+/i', '-', $text);
    $text = trim($text, '-');
    return $text !== '' ? $text : 'news';
}

function redirect_to($path)
{
    header("Location: {$path}");
    exit;
}

function query_all($sql, $params = [])
{
    $stmt = db()->prepare($sql);
    $stmt->execute($params);
    return $stmt->fetchAll();
}

function query_one($sql, $params = [])
{
    $stmt = db()->prepare($sql);
    $stmt->execute($params);
    $row = $stmt->fetch();
    return $row ?: null;
}

function execute_sql($sql, $params = [])
{
    $stmt = db()->prepare($sql);
    return $stmt->execute($params);
}

function menu_categories()
{
    return query_all("SELECT * FROM category WHERE status=1 AND menu_order > 0 ORDER BY menu_order ASC LIMIT 8");
}

function more_categories()
{
    return query_all("SELECT * FROM category WHERE status=1 AND menu_order = 0 ORDER BY category_name ASC");
}

function first_image_url($imageName)
{
    global $config;
    if ($imageName) {
        return $config['uploads_url'] . '/' . rawurlencode($imageName);
    }
    return '/static/no-image.jpg';
}

function require_admin()
{
    if (empty($_SESSION['admin_logged_in'])) {
        redirect_to('/admin');
    }
}

function page_header($title)
{
    global $config;
    $menus = menu_categories();
    $more = more_categories();
    ?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?= h($title) ?> | <?= h($config['site_name']) ?></title>
    <link rel="stylesheet" href="/static/css/news-theme.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body{font-family:Arial,Helvetica,sans-serif;background:#f5f5f5;color:#111}
        .container{max-width:1180px;margin:0 auto;padding:0 16px}
        .brandbar{background:#111;color:#fff}
        .brandbar a{color:#fff;text-decoration:none}
        .nav a{display:inline-block;padding:14px 10px;color:#fff;font-weight:700}
        .card{background:#fff;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.08);overflow:hidden}
        .card img{width:100%;height:190px;object-fit:cover}
        .btn{display:inline-block;background:#c1121f;color:#fff;padding:9px 14px;border-radius:6px;text-decoration:none;border:0;cursor:pointer}
        .btn.secondary{background:#333}
        .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px}
        input,select,textarea{width:100%;padding:10px;border:1px solid #ccc;border-radius:6px}
        table{width:100%;border-collapse:collapse;background:#fff}
        th,td{padding:10px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}
        .admin-nav a{margin-right:10px}
    </style>
</head>
<body>
<header class="brandbar">
    <div class="container" style="display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 16px">
        <a href="/" style="font-size:26px;font-weight:800"><?= h($config['site_name']) ?></a>
        <form action="/" method="get" style="display:flex;gap:8px;max-width:420px;width:100%">
            <input name="search" placeholder="Search news" value="<?= h($_GET['search'] ?? '') ?>">
            <button class="btn" type="submit">Search</button>
        </form>
    </div>
    <nav class="container nav">
        <a href="/">Home</a>
        <?php foreach ($menus as $cat): ?>
            <a href="/category/<?= (int)$cat['id'] ?>/<?= h(slugify($cat['category_name'])) ?>"><?= h($cat['category_name']) ?></a>
        <?php endforeach; ?>
        <?php foreach ($more as $cat): ?>
            <a href="/category/<?= (int)$cat['id'] ?>/<?= h(slugify($cat['category_name'])) ?>"><?= h($cat['category_name']) ?></a>
        <?php endforeach; ?>
        <a href="/admin">Admin</a>
    </nav>
</header>
<main class="container" style="padding:24px 16px">
    <?php
}

function page_footer()
{
    ?>
</main>
<footer style="background:#111;color:#fff;margin-top:30px;padding:24px 0">
    <div class="container">Noyyal Express</div>
</footer>
</body>
</html>
    <?php
}

function admin_header($title)
{
    page_header($title);
    require_admin();
    ?>
<div class="admin-nav card" style="padding:14px;margin-bottom:18px">
    <a class="btn secondary" href="/dashboard">Dashboard</a>
    <a class="btn secondary" href="/add-news">Add News</a>
    <a class="btn secondary" href="/news-list">News List</a>
    <a class="btn secondary" href="/analytics">Analytics</a>
    <a class="btn secondary" href="/logout">Logout</a>
</div>
    <?php
}

function route_home()
{
    $search = trim($_GET['search'] ?? '');
    $params = [];
    $where = '';
    if ($search !== '') {
        $where = "WHERE news.title LIKE ? OR news.description LIKE ? OR category.category_name LIKE ?";
        $kw = "%{$search}%";
        $params = [$kw, $kw, $kw];
    }

    $hero = query_all("SELECT news.*, MIN(news_images.image_name) AS image_name FROM news LEFT JOIN news_images ON news.id=news_images.news_id GROUP BY news.id ORDER BY news.id DESC LIMIT 5");
    $breaking = query_all("SELECT * FROM news WHERE is_breaking=1 ORDER BY id DESC LIMIT 10");
    $latest = query_all("SELECT news.*, category.category_name, MIN(news_images.image_name) AS image_name FROM news LEFT JOIN category ON news.category_id=category.id LEFT JOIN news_images ON news.id=news_images.news_id {$where} GROUP BY news.id ORDER BY news.id DESC LIMIT 20", $params);

    page_header('Home');
    ?>
<section class="card" style="padding:18px;margin-bottom:18px">
    <h1 style="font-size:30px;font-weight:800;margin-bottom:10px">Latest News</h1>
    <?php if ($breaking): ?>
        <div style="background:#c1121f;color:#fff;padding:10px;border-radius:6px">
            Breaking:
            <?php foreach ($breaking as $item): ?>
                <span style="margin-right:18px"><?= h($item['title']) ?></span>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>
</section>

<?php if ($hero): ?>
<section class="grid" style="margin-bottom:24px">
    <?php foreach ($hero as $news): ?>
        <a class="card" href="/news/<?= (int)$news['id'] ?>/<?= h($news['slug'] ?: slugify($news['title'])) ?>" style="text-decoration:none;color:#111">
            <img src="<?= h(first_image_url($news['image_name'] ?? '')) ?>" alt="">
            <div style="padding:14px">
                <h2 style="font-size:20px;font-weight:800"><?= h($news['title']) ?></h2>
            </div>
        </a>
    <?php endforeach; ?>
</section>
<?php endif; ?>

<section class="grid">
    <?php foreach ($latest as $news): ?>
        <a class="card" href="/news/<?= (int)$news['id'] ?>/<?= h($news['slug'] ?: slugify($news['title'])) ?>" style="text-decoration:none;color:#111">
            <img src="<?= h(first_image_url($news['image_name'] ?? '')) ?>" alt="">
            <div style="padding:14px">
                <div style="color:#c1121f;font-weight:700"><?= h($news['category_name'] ?? 'News') ?></div>
                <h2 style="font-size:19px;font-weight:800"><?= h($news['title']) ?></h2>
                <p><?= h(substr(strip_tags($news['description'] ?? ''), 0, 120)) ?></p>
            </div>
        </a>
    <?php endforeach; ?>
</section>
    <?php
    page_footer();
}

function route_news_detail($id)
{
    $news = query_one("SELECT news.*, category.category_name, MIN(news_images.image_name) AS image_name FROM news LEFT JOIN category ON news.category_id=category.id LEFT JOIN news_images ON news.id=news_images.news_id WHERE news.id=? GROUP BY news.id LIMIT 1", [$id]);
    if (!$news) {
        http_response_code(404);
        page_header('News Not Found');
        echo '<h1>News Not Found</h1>';
        page_footer();
        return;
    }

    execute_sql("UPDATE news SET tot_view=COALESCE(tot_view, 0)+1 WHERE id=?", [$id]);
    $related = query_all("SELECT news.*, MIN(news_images.image_name) AS image_name FROM news LEFT JOIN news_images ON news.id=news_images.news_id WHERE news.category_id=? AND news.id!=? GROUP BY news.id ORDER BY news.id DESC LIMIT 6", [$news['category_id'], $id]);

    page_header($news['title']);
    ?>
<article class="card" style="padding:22px;margin-bottom:22px">
    <div style="color:#c1121f;font-weight:800"><?= h($news['category_name'] ?? 'News') ?></div>
    <h1 style="font-size:36px;font-weight:900;margin:10px 0"><?= h($news['title']) ?></h1>
    <img src="<?= h(first_image_url($news['image_name'] ?? '')) ?>" alt="" style="width:100%;max-height:520px;object-fit:cover;border-radius:8px;margin:14px 0">
    <div style="font-size:18px;line-height:1.75"><?= $news['description'] ?? '' ?></div>
</article>

<h2 style="font-size:26px;font-weight:800;margin:18px 0">Related News</h2>
<section class="grid">
    <?php foreach ($related as $item): ?>
        <a class="card" href="/news/<?= (int)$item['id'] ?>/<?= h($item['slug'] ?: slugify($item['title'])) ?>" style="text-decoration:none;color:#111">
            <img src="<?= h(first_image_url($item['image_name'] ?? '')) ?>" alt="">
            <div style="padding:14px"><h3 style="font-weight:800"><?= h($item['title']) ?></h3></div>
        </a>
    <?php endforeach; ?>
</section>
    <?php
    page_footer();
}

function route_category($id)
{
    $category = query_one("SELECT * FROM category WHERE id=? LIMIT 1", [$id]);
    $items = query_all("SELECT news.*, MIN(news_images.image_name) AS image_name FROM news LEFT JOIN news_images ON news.id=news_images.news_id WHERE news.category_id=? GROUP BY news.id ORDER BY news.id DESC LIMIT 50", [$id]);

    page_header($category['category_name'] ?? 'Category');
    echo '<h1 style="font-size:32px;font-weight:900;margin-bottom:18px">' . h($category['category_name'] ?? 'Category') . '</h1>';
    echo '<section class="grid">';
    foreach ($items as $news) {
        echo '<a class="card" href="/news/' . (int)$news['id'] . '/' . h($news['slug'] ?: slugify($news['title'])) . '" style="text-decoration:none;color:#111">';
        echo '<img src="' . h(first_image_url($news['image_name'] ?? '')) . '" alt="">';
        echo '<div style="padding:14px"><h2 style="font-size:19px;font-weight:800">' . h($news['title']) . '</h2>';
        echo '<p>' . h(substr(strip_tags($news['description'] ?? ''), 0, 120)) . '</p></div></a>';
    }
    echo '</section>';
    page_footer();
}

function route_admin_login()
{
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $admin = query_one("SELECT * FROM user WHERE u_name=? AND p_name=? LIMIT 1", [
            $_POST['username'] ?? '',
            $_POST['password'] ?? '',
        ]);
        if ($admin) {
            $_SESSION['admin_logged_in'] = true;
            redirect_to('/dashboard');
        }
        $error = 'Invalid username or password';
    }

    page_header('Admin Login');
    ?>
<div class="card" style="max-width:420px;margin:40px auto;padding:24px">
    <h1 style="font-size:28px;font-weight:900;margin-bottom:18px">Admin Login</h1>
    <?php if (!empty($error)): ?><p style="color:#c1121f"><?= h($error) ?></p><?php endif; ?>
    <form method="post" action="/admin">
        <label>Username</label>
        <input name="username" required>
        <label style="display:block;margin-top:12px">Password</label>
        <input name="password" type="password" required>
        <button class="btn" style="margin-top:18px" type="submit">Login</button>
    </form>
</div>
    <?php
    page_footer();
}

function route_dashboard()
{
    admin_header('Dashboard');
    $totalNews = query_one("SELECT COUNT(*) AS total FROM news")['total'] ?? 0;
    $breaking = query_one("SELECT COUNT(*) AS total FROM news WHERE is_breaking=1")['total'] ?? 0;
    $categories = query_one("SELECT COUNT(*) AS total FROM category")['total'] ?? 0;
    ?>
<h1 style="font-size:32px;font-weight:900;margin-bottom:18px">Dashboard</h1>
<section class="grid">
    <div class="card" style="padding:20px"><h2>Total News</h2><strong style="font-size:34px"><?= h($totalNews) ?></strong></div>
    <div class="card" style="padding:20px"><h2>Breaking News</h2><strong style="font-size:34px"><?= h($breaking) ?></strong></div>
    <div class="card" style="padding:20px"><h2>Categories</h2><strong style="font-size:34px"><?= h($categories) ?></strong></div>
</section>
    <?php
    page_footer();
}

function news_form($news = null)
{
    $categories = query_all("SELECT * FROM category WHERE status=1 ORDER BY category_name ASC");
    $isEdit = $news !== null;
    ?>
<form class="card" style="padding:20px" method="post" enctype="multipart/form-data" action="<?= $isEdit ? '/update-news/' . (int)$news['id'] : '/save-news' ?>">
    <label>Title</label>
    <input name="title" value="<?= h($news['title'] ?? '') ?>" required>

    <label style="display:block;margin-top:12px">Category</label>
    <select name="category_id" required>
        <?php foreach ($categories as $cat): ?>
            <option value="<?= (int)$cat['id'] ?>" <?= ($news && (int)$news['category_id'] === (int)$cat['id']) ? 'selected' : '' ?>><?= h($cat['category_name']) ?></option>
        <?php endforeach; ?>
    </select>

    <input type="hidden" name="channel_id" value="<?= h($news['channel_id'] ?? 0) ?>">

    <label style="display:block;margin-top:12px">Description</label>
    <textarea name="description" rows="10" required><?= h($news['description'] ?? '') ?></textarea>

    <label style="display:block;margin-top:12px">Source</label>
    <input name="source" value="<?= h($news['source'] ?? '') ?>">

    <label style="display:block;margin-top:12px">Video Link</label>
    <input name="video_link" value="<?= h($news['video_link'] ?? '') ?>">

    <label style="display:block;margin-top:12px"><input type="checkbox" name="is_breaking" value="1" <?= !empty($news['is_breaking']) ? 'checked' : '' ?> style="width:auto"> Breaking</label>
    <label><input type="checkbox" name="is_public" value="1" <?= !isset($news) || !empty($news['is_public']) ? 'checked' : '' ?> style="width:auto"> Public</label>
    <label><input type="checkbox" name="send_notification" value="1" <?= !empty($news['notify']) ? 'checked' : '' ?> style="width:auto"> Send Notification</label>

    <?php if (!$isEdit): ?>
        <label style="display:block;margin-top:12px">Images</label>
        <input type="file" name="images[]" multiple>
    <?php endif; ?>

    <button class="btn" style="margin-top:18px" type="submit"><?= $isEdit ? 'Update' : 'Publish' ?></button>
</form>
    <?php
}

function route_add_news()
{
    admin_header('Add News');
    echo '<h1 style="font-size:30px;font-weight:900;margin-bottom:18px">Add News</h1>';
    news_form();
    page_footer();
}

function route_save_news()
{
    require_admin();
    $slug = slugify($_POST['title'] ?? '');
    execute_sql("INSERT INTO news(category_id, channel_id, title, slug, description, source, video_link, link_type, is_breaking, is_public, notify, status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", [
        (int)($_POST['category_id'] ?? 0),
        (int)($_POST['channel_id'] ?? 0),
        $_POST['title'] ?? '',
        $slug,
        $_POST['description'] ?? '',
        $_POST['source'] ?? null,
        $_POST['video_link'] ?? null,
        $_POST['video_type'] ?? null,
        isset($_POST['is_breaking']) ? 1 : 0,
        isset($_POST['is_public']) ? 1 : 0,
        isset($_POST['send_notification']) ? 1 : 0,
        1,
    ]);
    $newsId = db()->lastInsertId();
    save_uploaded_images($newsId);
    redirect_to('/news-list');
}

function save_uploaded_images($newsId)
{
    global $config;
    if (empty($_FILES['images']['name'][0])) {
        return;
    }
    if (!is_dir($config['uploads_dir'])) {
        mkdir($config['uploads_dir'], 0755, true);
    }
    foreach ($_FILES['images']['name'] as $i => $name) {
        if ($_FILES['images']['error'][$i] !== UPLOAD_ERR_OK) {
            continue;
        }
        $safe = preg_replace('/[^a-zA-Z0-9._-]/', '_', basename($name));
        $target = $config['uploads_dir'] . '/' . $safe;
        move_uploaded_file($_FILES['images']['tmp_name'][$i], $target);
        execute_sql("INSERT INTO news_images(news_id, image_name) VALUES(?,?)", [$newsId, $safe]);
    }
}

function route_news_list()
{
    admin_header('News List');
    $search = trim($_GET['search'] ?? '');
    $categoryId = (int)($_GET['category_id'] ?? 0);
    $params = [];
    $where = "WHERE 1=1";
    if ($search !== '') {
        $where .= " AND (news.title LIKE ? OR news.description LIKE ?)";
        $params[] = "%{$search}%";
        $params[] = "%{$search}%";
    }
    if ($categoryId > 0) {
        $where .= " AND news.category_id=?";
        $params[] = $categoryId;
    }
    $items = query_all("SELECT news.*, category.category_name, MIN(news_images.image_name) AS image_name FROM news LEFT JOIN category ON news.category_id=category.id LEFT JOIN news_images ON news.id=news_images.news_id {$where} GROUP BY news.id ORDER BY news.id DESC LIMIT 100", $params);
    $categories = query_all("SELECT * FROM category WHERE status=1 ORDER BY category_name ASC");
    ?>
<h1 style="font-size:30px;font-weight:900;margin-bottom:18px">News List</h1>
<form class="card" style="padding:14px;margin-bottom:16px;display:grid;grid-template-columns:1fr 220px auto;gap:10px" method="get" action="/news-list">
    <input name="search" placeholder="Search" value="<?= h($search) ?>">
    <select name="category_id">
        <option value="0">All categories</option>
        <?php foreach ($categories as $cat): ?>
            <option value="<?= (int)$cat['id'] ?>" <?= $categoryId === (int)$cat['id'] ? 'selected' : '' ?>><?= h($cat['category_name']) ?></option>
        <?php endforeach; ?>
    </select>
    <button class="btn" type="submit">Filter</button>
</form>
<table>
    <thead><tr><th>ID</th><th>Image</th><th>Title</th><th>Category</th><th>Views</th><th>Actions</th></tr></thead>
    <tbody>
    <?php foreach ($items as $news): ?>
        <tr>
            <td>#<?= (int)$news['id'] ?></td>
            <td><img src="<?= h(first_image_url($news['image_name'] ?? '')) ?>" style="width:90px;height:60px;object-fit:cover"></td>
            <td><?= h($news['title']) ?></td>
            <td><?= h($news['category_name'] ?? '') ?></td>
            <td><?= h($news['tot_view'] ?? 0) ?></td>
            <td>
                <a href="/edit-news/<?= (int)$news['id'] ?>">Edit</a> |
                <a href="/delete-news/<?= (int)$news['id'] ?>" onclick="return confirm('Delete this news?')">Delete</a>
            </td>
        </tr>
    <?php endforeach; ?>
    </tbody>
</table>
    <?php
    page_footer();
}

function route_edit_news($id)
{
    admin_header('Edit News');
    $news = query_one("SELECT * FROM news WHERE id=? LIMIT 1", [$id]);
    if (!$news) {
        echo '<h1>News Not Found</h1>';
    } else {
        echo '<h1 style="font-size:30px;font-weight:900;margin-bottom:18px">Edit News</h1>';
        news_form($news);
    }
    page_footer();
}

function route_update_news($id)
{
    require_admin();
    execute_sql("UPDATE news SET category_id=?, channel_id=?, title=?, slug=?, description=?, source=?, video_link=?, link_type=?, is_breaking=?, is_public=?, notify=? WHERE id=?", [
        (int)($_POST['category_id'] ?? 0),
        (int)($_POST['channel_id'] ?? 0),
        $_POST['title'] ?? '',
        slugify($_POST['title'] ?? ''),
        $_POST['description'] ?? '',
        $_POST['source'] ?? null,
        $_POST['video_link'] ?? null,
        $_POST['video_type'] ?? null,
        isset($_POST['is_breaking']) ? 1 : 0,
        isset($_POST['is_public']) ? 1 : 0,
        isset($_POST['send_notification']) ? 1 : 0,
        $id,
    ]);
    redirect_to('/news-list');
}

function route_delete_news($id)
{
    require_admin();
    execute_sql("DELETE FROM news_images WHERE news_id=?", [$id]);
    execute_sql("DELETE FROM news WHERE id=?", [$id]);
    redirect_to('/news-list');
}

function route_analytics()
{
    admin_header('Analytics');
    $totalNews = query_one("SELECT COUNT(*) AS total FROM news")['total'] ?? 0;
    $breaking = query_one("SELECT COUNT(*) AS total FROM news WHERE is_breaking=1")['total'] ?? 0;
    $views = query_one("SELECT SUM(tot_view) AS total FROM news")['total'] ?? 0;
    $top = query_all("SELECT title, tot_view FROM news ORDER BY tot_view DESC LIMIT 5");
    ?>
<h1 style="font-size:30px;font-weight:900;margin-bottom:18px">Analytics</h1>
<section class="grid" style="margin-bottom:18px">
    <div class="card" style="padding:20px"><h2>Total News</h2><strong style="font-size:34px"><?= h($totalNews) ?></strong></div>
    <div class="card" style="padding:20px"><h2>Breaking News</h2><strong style="font-size:34px"><?= h($breaking) ?></strong></div>
    <div class="card" style="padding:20px"><h2>Total Views</h2><strong style="font-size:34px"><?= h($views) ?></strong></div>
</section>
<table><thead><tr><th>Title</th><th>Views</th></tr></thead><tbody>
<?php foreach ($top as $item): ?>
    <tr><td><?= h($item['title']) ?></td><td><?= h($item['tot_view'] ?? 0) ?></td></tr>
<?php endforeach; ?>
</tbody></table>
    <?php
    page_footer();
}

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

try {
    if ($path === '/') {
        route_home();
    } elseif (preg_match('#^/news/(\d+)#', $path, $m)) {
        route_news_detail((int)$m[1]);
    } elseif (preg_match('#^/category/(\d+)#', $path, $m)) {
        route_category((int)$m[1]);
    } elseif ($path === '/admin') {
        route_admin_login();
    } elseif ($path === '/logout') {
        session_destroy();
        redirect_to('/admin');
    } elseif ($path === '/dashboard') {
        route_dashboard();
    } elseif ($path === '/add-news') {
        route_add_news();
    } elseif ($path === '/save-news' && $method === 'POST') {
        route_save_news();
    } elseif ($path === '/news-list') {
        route_news_list();
    } elseif (preg_match('#^/edit-news/(\d+)#', $path, $m)) {
        route_edit_news((int)$m[1]);
    } elseif (preg_match('#^/update-news/(\d+)#', $path, $m) && $method === 'POST') {
        route_update_news((int)$m[1]);
    } elseif (preg_match('#^/delete-news/(\d+)#', $path, $m)) {
        route_delete_news((int)$m[1]);
    } elseif ($path === '/analytics') {
        route_analytics();
    } else {
        http_response_code(404);
        page_header('Not Found');
        echo '<h1>Page Not Found</h1>';
        page_footer();
    }
} catch (Throwable $e) {
    http_response_code(500);
    echo '<h1>Noyyal Express PHP Error</h1>';
    echo '<pre>' . h($e->getMessage()) . "\n\n" . h($e->getTraceAsString()) . '</pre>';
}
