FROM python:2.7
ADD . /code
WORKDIR /code
RUN apt-get update
RUN apt-get install -y libzmq3-dev
RUN pip install -r requirements.txt
