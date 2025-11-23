FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Try installing without gcc first - modern Python packages have binary wheels
# If this fails, we'll need to add gcc back for cryptography/bcrypt compilation

# Copy requirements first for better Docker layer caching
# This layer will be cached unless requirements.txt changes
COPY requirements.txt .

# Install Python dependencies
# This will be slow on slow internet, but at least it's cached separately
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code last (changes most frequently)
COPY . .

EXPOSE 8195

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8195"]
