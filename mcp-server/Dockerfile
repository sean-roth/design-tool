FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 3000

# Run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
