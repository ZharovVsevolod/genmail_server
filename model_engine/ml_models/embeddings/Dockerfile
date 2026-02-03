FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

RUN apt-get update && apt-get -y upgrade

# Set working directory
WORKDIR /app


# Copy files for enviroment
COPY model_engine/ml_models/embeddings/uv.lock .
COPY model_engine/ml_models/embeddings/pyproject.toml .

# Build enviroment
RUN uv sync


# Build utils from gm_services
COPY gm_services/ .
RUN up pip install ./gm_services


# Copy the remainings
COPY model_engine/ml_models/embeddings/src/ .
COPY model_engine/ml_models/embeddings/main.py .
COPY .env .


EXPOSE 8003

# Run server
CMD ["uv", "run", "main.py"]