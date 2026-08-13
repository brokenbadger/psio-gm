# Built by Docker Compose (`docker compose up --build -d`).
# The app never runs as root: default USER is psio (uid 1000).
# Compose overrides with PUID:PGID so bind-mounted ./games files match the host user.

FROM python:3.11-slim

LABEL org.opencontainers.image.title="PSIO-GM" \
      org.opencontainers.image.version="0.2.2"

ENV PYTHONDONTWRITEBYTECODE=1

RUN groupadd --gid 1000 psio \
    && useradd --uid 1000 --gid 1000 --create-home --shell /usr/sbin/nologin psio

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src/ /app/src/

# DB merge writes into data/ at runtime; allow Compose PUID (any uid) to write
RUN chmod -R a+rwX /app/src/data \
    && chown -R psio:psio /app

WORKDIR /app/src

USER psio

CMD ["python", "-m", "webapp", "--host", "0.0.0.0", "--port", "5000"]
