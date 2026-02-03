FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

RUN apt-get update && apt-get -y upgrade

# Set working directory
WORKDIR /app


# Copy files for enviroment
COPY data_info_handler/retriever/uv.lock .
COPY data_info_handler/retriever/pyproject.toml .

# Build enviroment
RUN uv sync


# Build utils from gm_services
COPY gm_services/ .
RUN up pip install ./gm_services


# Copy the remainings
COPY data_info_handler/retriever/src/ .
COPY data_info_handler/retriever/main.py .
COPY .env .


EXPOSE 8004

# Run server
CMD ["uv", "run", "main.py"]