FROM python:3.9.1

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/
COPY . /usr/src/app/
RUN pip install -r requirements.txt

ENTRYPOINT uvicorn main:fastapp --reload --host 0.0.0.0 --port 8000
