FROM python:3.13-alpine

WORKDIR /app

RUN pip install --no-cache-dir uv

# Copy project files
RUN mkdir data_info_handler
COPY data_info_handler/document_handler/pyproject.toml .
COPY data_info_handler/document_handler/uv.lock .
COPY data_info_handler/document_handler /app/data_info_handler/document_handler
COPY gm_services /app/gm_services

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "--frozen", "--no-cache", "data_info_handler/document_handler/main.py"]