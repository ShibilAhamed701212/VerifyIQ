FROM python:3.11-slim AS builder

WORKDIR /build

COPY pyproject.toml VERSION README.md ./
COPY verifyiq/ ./verifyiq/
RUN pip install --no-cache-dir build && python -m build --wheel

RUN pip install --no-cache-dir -e ".[dev,api,dashboard]" && pip freeze > /build/requirements-full.txt

FROM python:3.11-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml VERSION README.md ./
COPY verifyiq/ ./verifyiq/
RUN pip install --no-cache-dir -e ".[api,dashboard]"

COPY code/ ./code/
COPY dataset/ ./dataset/

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

ENTRYPOINT ["verifyiq"]
CMD ["evaluate"]
