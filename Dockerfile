FROM python:3.12-slim

# Create app directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Make your script executable
RUN chmod +x /app/script.sh

# Default command does nothing — we'll trigger manually via `docker exec`
CMD ["sleep", "infinity"]
