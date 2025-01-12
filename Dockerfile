# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set AWS credentials as environment variables
ENV AWS_ACCESS_KEY_ID=AKIAUBKFCJSJC7G4E7XG
ENV AWS_SECRET_ACCESS_KEY=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
ENV AWS_REGION=ap-south-1

# Make port 5000 available to the outside world
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
