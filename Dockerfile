# HomeOS Multi-User Server Docker Image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements_v2.txt .
RUN pip install --no-cache-dir -r requirements_v2.txt

# Copy application
COPY server_v2.py .
COPY api_client.js .

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=server_v2.py
ENV PYTHONUNBUFFERED=1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "server_v2:app"]