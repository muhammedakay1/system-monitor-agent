FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
ENV DISK_PATH=/host
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN useradd -m appuser && chown -R appuser /app
COPY . .
USER appuser
CMD ["python","main.py","--auth-log","logs/sample_auth.log","--interval","60"]