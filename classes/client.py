from zeep import Client, Settings, xsd
from requests import Session
from requests.auth import AuthBase, HTTPBasicAuth
from zeep.transports import Transport
import os

def initialize_client(username, password):
        wsdl = os.environ.get('wsdl', None)
        sess = Session()
        transport = Transport(timeout=10, session=sess)
        sess.auth = HTTPBasicAuth(username, password)
        sess.verify = False
        client = Client(wsdl=wsdl, transport=transport)
        if client is None:
                return None
        client.transport.session.verify = False
        address = wsdl.replace("?wsdl", "")
        client.service._binding_options['address'] = address
        return client