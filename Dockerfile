FROM python:3.5-alpine
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD app/ /app
WORKDIR /app
ENTRYPOINT ["./app.py"]