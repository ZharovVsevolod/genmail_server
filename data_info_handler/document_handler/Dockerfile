# TODO(diduk001): не уверен в этом докерфайле, у меня не запускается по причине:
# ```

# ```
FROM python:3.10-alpine

WORKDIR /app

RUN pip install --no-cache-dir uv

# Copy project files
RUN mkdir data_info_handler
COPY data_info_handler/document_handler/pyproject.toml .
COPY data_info_handler/document_handler/uv.lock .
COPY data_info_handler/document_handler /app/data_info_handler/document_handler
COPY gm_services /app/gm_services

# Create venv andinstall gm_services
ENV VIRTUAL_ENV=.venv

RUN ["uv", "pip", "install", "/app/gm_services"]

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "--active", "--frozen", "--no-cache", "data_info_handler/document_handler/main.py"]