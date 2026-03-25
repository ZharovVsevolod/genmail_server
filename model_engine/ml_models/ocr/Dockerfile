FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

RUN apt-get update && apt-get -y upgrade

# Set working directory
WORKDIR /app


# Copy files for enviroment (reuse embeddings env)
COPY model_engine/ml_models/ocr/uv.lock .
COPY model_engine/ml_models/ocr/pyproject.toml .

# Build enviroment
RUN uv sync


# Build utils from gm_services
COPY gm_services/ ./gm_services
RUN uv pip install ./gm_services

# Extra deps for OCR service
RUN python -m pip install --no-cache-dir uvicorn fastapi openai pypdf2 pymupdf


# Copy the remainings
COPY model_engine/ml_models/ocr/src/ .
COPY model_engine/ml_models/assets/ ./assets
COPY model_engine/ml_models/ocr/main.py .
COPY model_engine/ml_models/ocr/test.py .
# COPY .env .


EXPOSE 8004

# Run server
CMD ["python", "main.py"]

