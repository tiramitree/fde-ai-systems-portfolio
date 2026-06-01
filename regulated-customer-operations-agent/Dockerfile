FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

EXPOSE 8770
CMD ["python", "-B", "app.py", "--reset", "--host", "0.0.0.0", "--port", "8770"]

