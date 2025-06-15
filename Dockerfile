# Use official Python 3.9 slim image as base
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy your entire project code into /app
COPY . .

# ✅ Let Python find your 'src' package
ENV PYTHONPATH="/app"

# Default command to run your scraper script
CMD ["python3", "src/main.py"]

