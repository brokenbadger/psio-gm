# Built by Docker Compose only (`docker compose up --build`).
# Prefer a local Python 3.9+ venv with Tk for everyday use.

FROM python:3.11-slim

LABEL org.opencontainers.image.title="PSIO-GM" \
      org.opencontainers.image.version="0.1"

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-tk tk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src/ /app/src/

WORKDIR /app/src

CMD ["python", "psio_gm.py"]
