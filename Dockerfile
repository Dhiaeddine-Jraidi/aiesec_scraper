FROM selenium/standalone-chrome:latest

WORKDIR /scraper_2.0

COPY . /scraper_2.0

USER root

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install -r requirements.txt

CMD python3 main.py