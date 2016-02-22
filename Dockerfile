FROM debian:jessie

MAINTAINER François "francois.vanderbiest@camptocamp.com"

RUN apt-get update && \
    apt-get install -y python2.7 python2.7-dev python-pip libxslt1-dev lib32z1-dev && \
		rm -rf /var/lib/apt/lists/*

ADD test_extractorapp.py /tmp

RUN pip install httplib2 simplejson lxml

CMD python /tmp/test_extractorapp.py