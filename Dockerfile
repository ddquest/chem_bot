FROM kubor/alpine-rdkit:latest

MAINTAINER kubor

COPY . /chem_bot

WORKDIR /chem_bot/java
RUN sh get_opsin.sh

RUN apk update && \
    apk --no-cache add openjdk8

WORKDIR /chem_bot
RUN pip install -r requirements.txt

RUN pip install -e .

CMD ["python", "-u", "bin/run_twitter_client.py"]
