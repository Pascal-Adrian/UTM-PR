FROM python:3.9.20-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8000
EXPOSE 8001

CMD ["python", "main.py"]