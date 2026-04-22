FROM python:3.14-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache libpq

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev \
    libffi-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

COPY . .

EXPOSE 5000

ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]
