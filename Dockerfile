FROM python:3.8.3-slim

RUN apt-get update
RUN apt-get dist-upgrade -y

RUN apt-get install -y \
  build-essential \
  curl

RUN mkdir -p /app
WORKDIR /app

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
COPY pyproject.toml poetry.lock ./

ENV PATH="/root/.poetry/bin:$PATH"
RUN bash -c "poetry export -f requirements.txt > requirements.txt"
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "sevro/main.py"]
