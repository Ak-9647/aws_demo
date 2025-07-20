# Production analytics agent for AgentCore - HTTP Server
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY app.py .
COPY analytics_engine.py .

# Set environment variables
ENV PYTHONPATH=/app
ENV AWS_DEFAULT_REGION=us-west-2
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run the HTTP server
CMD ["python", "main.py"]