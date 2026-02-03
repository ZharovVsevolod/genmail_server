FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

RUN apt-get update && apt-get -y upgrade

# Set working directory
WORKDIR /app


# Copy files for enviroment
COPY data_info_handler/document_handler/uv.lock .
COPY data_info_handler/document_handler/pyproject.toml .

# Build enviroment
RUN uv sync


# Build utils from gm_services
COPY gm_services/ .
RUN up pip install ./gm_services


# Copy the remainings
COPY data_info_handler/document_handler/models/ .
COPY data_info_handler/document_handler/routes/ .
COPY data_info_handler/document_handler/services/ .
COPY backend_head/app.py .
COPY backend_head/main.py .
COPY .env .


EXPOSE 8002

# Run server
CMD ["uv", "run", "main.py"]