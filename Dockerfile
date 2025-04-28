# Use an official Python runtime
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy project files into the container
COPY . .

# Install project dependencies from requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Download necessary NLTK data
RUN python -m nltk.downloader punkt

# Expose the port uvicorn will run on
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]