FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl

# Create app directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Make your script executable
# RUN chmod +x /app/script.sh

# Default command does nothing — we'll trigger manually via `docker exec`
# CMD ["sleep", "infinity"]
# CMD ["bash", "script.sh"]
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "5000"]


