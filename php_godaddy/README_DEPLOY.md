# Noyyal Express PHP Deployment

This folder is a PHP version of the Noyyal Express Platform for GoDaddy shared hosting.

## Upload

Upload the contents of `php_godaddy` into GoDaddy `public_html`.

Also copy your existing `static` folder into `public_html/static`.

Final structure:

```text
public_html/index.php
public_html/config.php
public_html/.htaccess
public_html/static/
```

## Configure Database

Edit `public_html/config.php` and set:

```php
'db_name' => 'noyyalexpress',
'db_user' => 'noyyalexpress_admin',
'db_pass' => 'YOUR_DATABASE_PASSWORD',
```

## URLs

```text
/
/news/{id}/{slug}
/category/{id}/{slug}
/admin
/dashboard
/add-news
/news-list
/analytics
```

## Notes

- This PHP version uses the existing MySQL tables.
- It does not need Python, Passenger, pip, FastAPI, or virtualenv.
- Use cPanel File Manager and normal GoDaddy PHP hosting.
