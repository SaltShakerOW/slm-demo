FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./src ./src

EXPOSE 5000

CMD ["flask", "--app", "./src/server.py", "run", "--host", "0.0.0.0"]