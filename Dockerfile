FROM python:3.11-slim

ARG VERSION=dev
ENV APP_VERSION=$VERSION

WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY app /app/app
COPY static /app/static
COPY config /app/config

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8787

CMD ["uvicorn", "app.web:app", "--host", "0.0.0.0", "--port", "8787"]