# Note: this is a Tkinter GUI app. Running it in Docker requires a display
# (e.g. X11 forwarding) and is not the recommended way to use the tool.
# Prefer a local Python 3.9+ venv with Tk installed on the host.

FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-tk tk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src/ /app/src/

WORKDIR /app/src

CMD ["python", "psio_gm.py"]
