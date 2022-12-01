ARG python-version=3.9
FROM python:${python-version}-slim
LABEL org.opencontainers.image.authors="Timothy Ellersiek <timothy@openrouteservice.org>"

# protobuf is required to parse osm files.
# git to install imposm-parser via pip from github
# build-essential to build imposm-parser
RUN apt-get update && apt-get install -y libprotobuf-dev protobuf-compiler locales git build-essential
# update pip
RUN /usr/local/bin/python -m pip install --upgrade pip
# update Certificates, see: https://stackoverflow.com/questions/73820074/module-lib-has-no-attribute-x509-v-flag-cb-issuer-check-when-running-any-pip
# but also https://stackoverflow.com/questions/73861078/scrapy-attributeerror-module-openssl-ssl
RUN pip3 install pyOpenSSL==22.0.0 --upgrade

# used by GeoFabricSpider.py
RUN apt-get install wget

# Set the locale
ENV LANG=C.UTF-8 LANGUAGE=C:en LC_ALL=C.UTF-8

# Setup flask application
WORKDIR /deploy/app
COPY requirements.txt ./
RUN pip3 install -r /deploy/app/requirements.txt
COPY gunicorn_config.py run.sh manage.py ./
COPY openpoiservice ./openpoiservice

EXPOSE 5000
ENTRYPOINT ["/bin/bash", "run.sh"]
