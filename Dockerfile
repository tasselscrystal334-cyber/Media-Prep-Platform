FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg mediainfo \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt README.md /app/
COPY mediaqc /app/mediaqc
COPY profiles /app/profiles
COPY config /app/config

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -e ".[enterprise]"

EXPOSE 8080

CMD ["mediaqc", "enterprise-api", "--host", "0.0.0.0", "--port", "8080"]
