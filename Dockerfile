FROM oraclelinux:7-slim
MAINTAINER Christopher "cshannon@ufl.edu"

# INSTALL ORACLE DEPENDENCIES
RUN yum -y install oracle-release-el7 oraclelinux-developer-release-el7 && \
    yum -y install java-11-openjdk-devel && \
    yum -y install python3 \
                   python3-libs \
                   python3-pip \
                   python3-setuptools
                   
RUN yum -y install oracle-instantclient19.11-basic

RUN rm -rf /var/cache/yum/*

RUN mkdir /oracle_wallet

# COPY APP AND LOCAL DEPENDENCIES
COPY . /app

# CONFIGURE SQLCL
RUN mv /app/sqlcl /usr/bin/
ENV SQLCL_HOME="/usr/bin/sqlcl/"

# CONFIGURE JAVA CLASSPATH
ENV CLASSPATH=${SQLCL_HOME}/lib/oraclepki.jar:${SQLCL_HOME}/lib/osdt_core.jar:${SQLCL_HOME}/lib/osdt_cert.jar

WORKDIR /app
RUN pip3 install -r /app/requirements.txt

EXPOSE 5000

CMD ["/bin/bash", "/app/start_app.sh"]

