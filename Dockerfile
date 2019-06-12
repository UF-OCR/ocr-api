# INSTALL PYTHON IMAGE
FROM python:3.6
MAINTAINER Harshita "hkoranne@ufl.edu"

# INSTALL TOOLS
RUN apt-get update \
    && apt-get -y install unzip \
    && apt-get -y install libaio-dev \
    && apt-get -y install sudo \
    && mkdir -p /opt/data/ocr_api


ADD . /opt/data/ocr_api
WORKDIR /opt/data/ocr_api

ENV ORACLE_HOME=/opt/oracle/instantclient_12_1
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME

ENV OCI_HOME=/opt/oracle/instantclient_12_1
ENV OCI_LIB_DIR=/opt/oracle/instantclient_12_1
ENV OCI_INCLUDE_DIR=/opt/oracle/instantclient_12_1/sdk/include

RUN chmod +x ./install-instantclient.sh

# INSTALL INSTANTCLIENT AND DEPENDENCIES
RUN ./install-instantclient.sh \
    && pip install -r requirements.txt

EXPOSE 5000

CMD ["python","/opt/data/ocr_api/app.py"]