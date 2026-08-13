# Built by Docker Compose only (`docker compose up --build`).
# GUI profile needs X11; web profile is the recommended container use case.

FROM python:3.11-slim

LABEL org.opencontainers.image.title="PSIO-GM" \
      org.opencontainers.image.version="0.2.1"

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-tk tk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src/ /app/src/

WORKDIR /app/src

CMD ["python", "psio_gm.py"]
