FROM python:3.11-slim

WORKDIR /app

COPY requirements-prod.txt .

RUN pip install --no-cache-dir -r requirements-prod.txt

COPY . .

EXPOSE 8000

# Change from this:
# CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]

# To this:
CMD ["python", "-m", "uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]