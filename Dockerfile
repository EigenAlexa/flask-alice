FROM ubuntu:latest
MAINTAINER James Bartlett "james@ml.berkeley.edu"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential libssl-dev libffi-dev
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["rest_app.py"]
EXPOSE 80

