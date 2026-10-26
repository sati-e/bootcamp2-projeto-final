FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    DATA_DIR=/app/data

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 \
      fontconfig fonts-liberation fonts-montserrat \
 && rm -rf /var/lib/apt/lists/*

ADD https://raw.githubusercontent.com/google/fonts/main/ofl/greatvibes/GreatVibes-Regular.ttf /usr/local/share/fonts/GreatVibes-Regular.ttf
ADD https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/Caveat%5Bwght%5D.ttf /usr/local/share/fonts/Caveat.ttf
RUN chmod 644 /usr/local/share/fonts/*.ttf && fc-cache -f

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY frontend ./frontend

RUN useradd --create-home --uid 10001 app \
 && mkdir -p "$DATA_DIR" \
 && chown -R app:app "$DATA_DIR"
USER app
VOLUME ["/app/data"]

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/health' % os.environ['PORT'], timeout=3)"

CMD ["python", "-m", "backend.server"]