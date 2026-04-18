FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install fastapi uvicorn requests pydantic

# Copy code
COPY api.py .

# Run the API
EXPOSE 8050
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8050"]
