FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy job script
COPY vector_backfill_job.py .

# Run the job
CMD ["python", "vector_backfill_job.py"]