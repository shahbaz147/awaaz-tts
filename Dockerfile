FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Hugging Face Spaces & cloud platforms default port
ENV PORT=7860
EXPOSE 7860

CMD ["gunicorn", "app:app", "--worker-class", "gthread", "--workers", "2", "--threads", "4", "--timeout", "120", "--bind", "0.0.0.0:7860"]

