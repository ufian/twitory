FROM python:2.7-slim
ADD requirements.txt /app/src/
WORKDIR /app/src
RUN pip install -r requirements.txt
WORKDIR /app
EXPOSE 80
