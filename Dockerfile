FROM python:3.8-slim-buster

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
