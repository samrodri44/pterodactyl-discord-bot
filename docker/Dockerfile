FROM python:3.14.4-slim
 
# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
 
# Set workdir
WORKDIR /app
 
# System deps (keep minimal)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
 
# Copy dependency file first (better cache usage)
COPY requirements.txt .
 
# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
 
# Install dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
 
# Copy the rest of the project
COPY . .
 
# Default command
CMD ["python","src/bot/main.py","run"]
