FROM python:3.12-slim@sha256:090ba77e2958f6af52a5341f788b50b032dd4ca28377d2893dcf1ecbdfdfe203

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

EXPOSE 8765
CMD ["python", "-B", "app.py", "--reset", "--host", "0.0.0.0", "--port", "8765"]
