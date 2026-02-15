FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static
COPY webhook ./webhook
COPY start.py ./start.py

ENV PYTHONUNBUFFERED=1
EXPOSE 8000 8001

CMD ["python", "start.py"]
