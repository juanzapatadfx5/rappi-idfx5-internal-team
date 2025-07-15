# Use a lightweight Python base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
# Ensure requirements.txt is at the root of your build context
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code from the 'app' subdirectory to the WORKDIR
# This ensures main.py is directly in /app inside the container
COPY app/ .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
