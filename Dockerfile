FROM kubor/alpine-rdkit:latest

MAINTAINER kubor

COPY . /chem_bot

WORKDIR /chem_bot

ENV LC_ALL=C

RUN python setup.py install && \
    (cd java/ && sh get_opsin.sh)

CMD ["python", "-u", "/chem_bot/bin/run_twitter_client.py"]
