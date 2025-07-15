# Use a lightweight Python base image
FROM python:3.9-slim-buster

# Set the working directory in the container
# This will be /app as per App Runner's default behavior,
# and your app code will be in /app/app
WORKDIR /app

# Copy the requirements file and install dependencies
# Ensure requirements.txt is at the root of your build context
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code.
# Given your local structure (app/main.py), this will place it at /app/app/main.py
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI application with Uvicorn
# We explicitly tell Uvicorn to look inside the 'app' directory for 'main:app'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
