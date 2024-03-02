FROM python:3

# Set working directory
WORKDIR /usr/src/app

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "run.py", "0.0.0.0:8000"]
