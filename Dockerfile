# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set a working directory for your app
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port that FastAPI runs on
EXPOSE 8000

# Command to run the application using uvicorn
CMD ["uvicorn", "main_complete:app", "--host", "0.0.0.0", "--port", "8000"]

