# Use the official Python image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Set the PYTHONPATH to ensure Python can find the app module
ENV PYTHONPATH=/app

# Copy the requirements.txt first to leverage Docker layer caching
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project into the container
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
