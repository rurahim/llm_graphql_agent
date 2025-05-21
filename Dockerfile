FROM mcr.microsoft.com/azure-functions/python:4-python3.9

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 8000

# Set environment variable to disable Uvicorn access logs
ENV UVICORN_ACCESS_LOG=false

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]