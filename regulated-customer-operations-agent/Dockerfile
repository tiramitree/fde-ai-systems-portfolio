FROM python:3.12-slim@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

EXPOSE 8770
CMD ["python", "-B", "app.py", "--reset", "--host", "0.0.0.0", "--port", "8770"]
