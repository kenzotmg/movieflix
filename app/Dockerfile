FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 10001 appuser
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./app/

USER appuser
EXPOSE 8000

# wsgi:app -> app/wsgi.py com "app = create_app()"
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app.wsgi:app"]
