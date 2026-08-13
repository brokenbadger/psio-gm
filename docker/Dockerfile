# Built by Docker Compose (`docker compose up --build`).
# End-user runtime is the Flask web UI only (no Tk / X11).

FROM python:3.11-slim

LABEL org.opencontainers.image.title="PSIO-GM" \
      org.opencontainers.image.version="0.2.2"

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src/ /app/src/

WORKDIR /app/src

CMD ["python", "-m", "webapp", "--host", "0.0.0.0", "--port", "5000"]
