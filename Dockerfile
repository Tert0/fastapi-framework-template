FROM python:3.9-alpine

RUN apk add --no-cache build-base musl-dev gcc yaml-dev

RUN pip install pipenv

WORKDIR /app

COPY Pipfile .

COPY Pipfile.lock .

RUN python -m pipenv install --system --deploy

COPY start.sh .

COPY app/ ./app

COPY config.yaml .

CMD chmod +x start.sh && ./start.sh