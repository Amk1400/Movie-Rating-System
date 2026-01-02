FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# کپی بسته‌های .deb به کانتینر
COPY debs /tmp/debs

# نصب بسته‌های .deb آفلاین
RUN dpkg -i /tmp/debs/*.deb || apt-get install -f -y

# کپی wheelهای آفلاین
COPY wheels /wheels

# کپی requirements
COPY requirements.txt /app/

# نصب پکیج‌های پایتون به صورت آفلاین
RUN pip install --no-index --find-links=/wheels -r requirements.txt

# کپی کل پروژه
COPY . /app

# فرمان اجرای برنامه
CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]
