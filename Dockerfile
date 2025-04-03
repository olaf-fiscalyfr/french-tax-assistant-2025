
# Dockerfile for French Tax Assistant 2025

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y     build-essential     libpoppler-cpp-dev     && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
