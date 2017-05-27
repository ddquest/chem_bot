FROM kubor/alpine-rdkit:latest

MAINTAINER kubor

COPY . /chem_bot

WORKDIR /chem_bot

ENV LC_ALL=C

RUN python setup.py install && \
    (cd java/ && sh get_opsin.sh)

RUN apk update && \
    apk --no-cache add openjdk8

CMD ["python", "-u", "bin/run_twitter_client.py"]
