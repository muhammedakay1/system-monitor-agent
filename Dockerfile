FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN useradd -m appuser && chown -R appuser /app
USER appuser
COPY . .
CMD ["python","main.py","--auth-log","logs/sample_auth.log"]