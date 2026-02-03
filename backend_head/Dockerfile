FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

RUN apt-get update && apt-get -y upgrade

# Set working directory
WORKDIR /app


# Copy files for enviroment
COPY backend_head/uv.lock .
COPY backend_head/pyproject.toml .

# Build enviroment
RUN uv sync


# Build utils from gm_services
COPY gm_services/ .
RUN up pip install ./gm_services


# Copy the remainings
RUN mkdir backend_head
COPY backend_head/src/ ./backend_head/
COPY backend_head/main.py .
COPY .env .


EXPOSE 1702

# Run server
CMD ["uv", "run", "main.py"]