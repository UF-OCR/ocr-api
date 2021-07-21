#!/bin/sh
#CREATE EMPTY ORACLE WALLET
java -classpath ${CLASSPATH} oracle.security.pki.textui.OraclePKITextUI "$@" wallet create -wallet /oracle_wallet -auto_login -pwd $WALLET_PASSWORD;
#ADD TRUSTEDROOT CERTIFICATE TO WALLET
java -classpath ${CLASSPATH} oracle.security.pki.textui.OraclePKITextUI "$@" wallet add -wallet /oracle_wallet/ -trusted_cert -cert /usr/lib/oracle/19.11/client64/lib/network/admin/TrustedRoot.crt -pwd $WALLET_PASSWORD;
#RUN APPLICATION
python3 /app/app.py;

