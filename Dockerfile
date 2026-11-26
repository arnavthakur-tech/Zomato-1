FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

COPY requirements-api.txt .
RUN pip install --upgrade pip && pip install -r requirements-api.txt

COPY . .

EXPOSE 8000

# Use Python entrypoint so PORT is read from env (avoids literal `$PORT` crashes).
CMD ["python", "start.py"]
