FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

COPY requirements-api.txt .
RUN pip install --upgrade pip && pip install -r requirements-api.txt

# Railway dashboard may still run `uvicorn ... --port $PORT` (literal).
# Replace the uvicorn console script with a shim that reads env PORT.
COPY scripts/uvicorn_port_shim.py /usr/local/bin/uvicorn
RUN chmod +x /usr/local/bin/uvicorn

COPY . .

EXPOSE 8000

CMD ["python", "start.py"]
