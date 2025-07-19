# Simple single-stage build for production analytics agent
FROM public.ecr.aws/lambda/python:3.13-arm64

# Set working directory
WORKDIR /var/task

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set the handler
CMD ["main.handler"]