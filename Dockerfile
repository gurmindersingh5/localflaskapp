FROM python:3

# Copy the rest of the application
COPY . .

# Install dependencies
RUN pip install -r requirements.txt


# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "run.py", "0.0.0.0:8000"]
