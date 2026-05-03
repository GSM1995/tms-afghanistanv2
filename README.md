# سیستم مدیریت حمل و نقل (TMS) - افغانستان

سیستم جامع مدیریت حمل و نقل، سفارشات، ردیابی خودروها و مدیریت مالی

## قابلیت‌ها
- مدیریت مشتریان، رانندگان، خودروها
- مدیریت سفارشات و اسناد
- مدیریت مالی (فاکتورها و پرداخت‌ها)
- ردیابی لحظه‌ای خودروها روی نقشه
- پنل اختصاصی مشتریان و رانندگان
- سیستم نقش‌های کاربری و دسترسی‌ها

## نصب و راه‌اندازی

```bash
# کلون پروژه
git clone <your-repo-url>
cd tms

# ایجاد محیط مجازی
python -m venv venv

# فعال کردن محیط مجازی
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# نصب پیش‌نیازها
pip install -r requirements.txt

# اجرای مایگریشن‌ها
python manage.py migrate

# ایجاد سوپر یوزر
python manage.py createsuperuser

# اجرای سرور
python manage.py runserver