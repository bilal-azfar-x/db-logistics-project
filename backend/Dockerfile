FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# IMPORTANT:
# Seeder is run manually ONCE.
# API should NEVER reseed on restart.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
