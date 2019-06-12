#!/usr/bin/env bash
mkdir /opt/oracle
mkdir /opt/oracle/instantclient
unzip /opt/data/ocr_api/oracle-instantclient/instantclient-basic-linux.x64-12.1.0.2.0.zip -d /opt/oracle
unzip /opt/data/ocr_api/oracle-instantclient/instantclient-sdk-linux.x64-12.1.0.2.0.zip -d /opt/oracle
ln -s /opt/oracle/instantclient_12_1/libclntsh.so.12.1 /opt/oracle/instantclient_12_1/libclntsh.so
ln -s /opt/oracle/instantclient_12_1/libocci.so.12.1 /opt/oracle/instantclient_12_1/libocci.so

export ORACLE_HOME="/opt/oracle/instantclient_12_1"
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME

export OCI_HOME="/opt/oracle/instantclient_12_1"
export OCI_LIB_DIR="/opt/oracle/instantclient_12_1"
export OCI_INCLUDE_DIR="/opt/oracle/instantclient_12_1/sdk/include"

sudo ldconfig