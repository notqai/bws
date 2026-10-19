# BWS Portal

A small Laravel app that sits beside the static website (`../site`). It provides:

- **Vacancies** that HR publishes from the admin panel. They appear on the website's Careers page until their closing date.
- **Online job applications** with CV upload (PDF or Word, up to 5 MB) from the Careers page, with consent to the Privacy Notice recorded on each one.
- **An admin panel** for HR: list, filter and search applications, download CVs, track status and notes, delete on request, and manage vacancies.
- **PDPA retention:** applications and their CVs are deleted automatically after 12 months (`PORTAL_RETENTION_MONTHS`).

The website keeps working if the portal is down or not yet deployed: the Careers page hides the online form and shows only the "Send your CV" email option.

## How it fits together

```
www.bwsengineeringsb.com      static site (../site)   careers.html calls the API below with fetch()
portal.bwsengineeringsb.com   this app                GET  /api/vacancies     open vacancies (JSON)
                                                      POST /api/applications  application + CV
                                                      /admin                  HR admin panel (login)
```

- CVs are stored in `storage/app/private/cvs/` under random names. They are never publicly reachable; they can only be downloaded through the admin panel after login.
- HR gets an email for each new application, with a link to it in the admin panel. The CV is not attached, so it stays behind the login. Replying to the email answers the applicant.
- Only the origins in `PORTAL_SITE_ORIGINS` may call the API from a browser (CORS). Applications are limited to 5 per visitor per hour, and logins to 5 attempts per minute.

## Requirements

PHP 8.3 or newer with the usual Laravel extensions (pdo_mysql, mbstring, openssl, fileinfo, tokenizer, xml, ctype), MySQL or MariaDB, and Composer. Most cPanel hosts provide these; choose PHP 8.3+ in *MultiPHP Manager*.

## Deploy on cPanel

1. **Subdomain:** in *Domains*, create `portal.bwsengineeringsb.com` with its document root set to `portal/public` (for example `/home/<user>/portal/public`). Turn on *Force HTTPS* and make sure AutoSSL has issued a certificate.
2. **Database:** in *MySQL Databases*, create a database and a user with all privileges on it.
3. **Email:** in *Email Accounts*, create a sending address such as `website@bwsengineeringsb.com`, and note its SMTP settings (*Connect Devices*).
4. **Upload the code** to `/home/<user>/portal`:
   - With SSH (Terminal in cPanel): `git clone` the repo or upload this folder, then run `composer install --no-dev --optimize-autoloader`.
   - Without SSH: run `composer install --no-dev --optimize-autoloader` on your own computer, then upload the whole folder including `vendor/`.
5. **Configure:** copy `.env.example` to `.env` and set:
   ```
   APP_ENV=production
   APP_DEBUG=false
   APP_URL=https://portal.bwsengineeringsb.com
   SESSION_SECURE_COOKIE=true
   DB_CONNECTION=mysql
   DB_HOST=localhost
   DB_DATABASE=...   DB_USERNAME=...   DB_PASSWORD=...
   MAIL_MAILER=smtp
   MAIL_HOST=mail.bwsengineeringsb.com   MAIL_PORT=465   MAIL_SCHEME=smtps
   MAIL_USERNAME=website@bwsengineeringsb.com   MAIL_PASSWORD=...
   MAIL_FROM_ADDRESS=website@bwsengineeringsb.com
   MAIL_FROM_NAME="BWS Engineering"
   PORTAL_HR_EMAIL=bwsesbhr@gmail.com
   ```
6. **Set up** (Terminal):
   ```
   php artisan key:generate
   php artisan migrate --force
   php artisan portal:user hr@bwsengineeringsb.com --name="HR"   # asks for a password (12+ characters)
   php artisan config:cache && php artisan route:cache && php artisan view:cache
   ```
   Run `portal:user` again with the same email to reset a password, or with another email to add a second login.
7. **Daily clean-up:** in *Cron Jobs*, add (once a day is enough):
   `15 2 * * * cd /home/<user>/portal && php artisan schedule:run >> /dev/null 2>&1`
8. **Test:** open `https://portal.bwsengineeringsb.com` and log in, publish a test vacancy, check it appears on the website's Careers page, apply with a test CV, and confirm the email reaches HR. Then delete the test application.

After changing `.env` later, run `php artisan config:cache` again.

## Day-to-day use (HR)

- **Vacancies → Add vacancy.** Tick *Show on the website* to publish. It disappears from the website by itself after the closing date; leave the date empty to keep it open.
- **Applications.** New ones are marked *New*. Open one to download the CV, set the status (Reviewing, Shortlisted, Interview, Hired, Not suitable) and add internal notes.
- **Requests from applicants.** If someone asks to see, correct or delete their data, use the application page; *Delete application and CV* removes both permanently. The Privacy Notice promises a reply within 21 days.

## Development

```
composer install
cp .env.example .env && php artisan key:generate
touch database/database.sqlite && php artisan migrate
php artisan portal:user you@example.com
php artisan serve                 # http://127.0.0.1:8000
php artisan test                  # feature tests
vendor/bin/pint                   # code style
```

To try the Careers form locally, serve `../site` (e.g. `python3 -m http.server 8097` in that folder), point `PORTAL` in `../tools/generate_site.py` at `http://127.0.0.1:8000` (don't commit that), and set `PORTAL_SITE_ORIGINS=http://127.0.0.1:8097` in `.env`.

## Where things are

| | |
|---|---|
| `config/portal.php` | HR email, allowed website origins, retention period, privacy notice version, upload limits |
| `routes/api.php`, `app/Http/Controllers/Api/` | Public API used by the Careers page |
| `routes/web.php`, `app/Http/Controllers/Admin/` | Login and admin panel |
| `resources/views/admin/`, `public/css/admin.css` | Admin pages and styles (plain CSS, no build step) |
| `app/Mail/NewApplication.php`, `resources/views/mail/` | Email sent to HR |
| `app/Console/Commands/` | `portal:user` (logins) and `portal:prune-applications` (retention) |
| `tests/Feature/` | Tests for the API, admin panel and commands |
