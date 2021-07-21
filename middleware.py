from flask import jsonify
from flask import Response
from functools import wraps
from flask import request, abort
from cachelib.simple import SimpleCache
import logging
import json
from data_provider_service import DataProviderService
from flask import make_response
import hashlib
import datetime
import time
import os

logging.basicConfig(filename=os.environ.get('log_file', None), level=logging.DEBUG)

cache = SimpleCache()

oracle_connection_string = 'oracle+cx_oracle://{username}:{password}@{tns_name}'

db_engine = oracle_connection_string.format(
    username=os.environ.get('ORACLE_USERNAME', None),
    password=os.environ.get('ORACLE_PASSWORD', None),
    tns_name=os.environ.get('ORACLE_TNS_NAME', None)
)

def log_details(username, validated, op_type):
    call_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d%H:%M:%S')
    ip_address = request.remote_addr
    data_provider = DataProviderService(db_engine)
    log_details_id = data_provider.log_details(username, ip_address, call_time, validated, op_type)
    data_provider.close_connection()
    return log_details_id

def require_app_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        tokens = os.environ.get('api_tokens', None)
        tokens = json.loads(tokens)
        username = request.headers.get('x-api-user')
        key = request.headers.get('x-api-key')
        password = None
        if username in tokens:
            password = tokens[username]
        if key and password and key == password and username and tokens[username]:
            logging.info("Validated")
            return view_function(*args, **kwargs)
        else:
            logging.info("Validation failed")
            abort(401)
    return decorated_function

@require_app_key
def get_ocr_protocols():
    cp = cache.get('protocol-list')
    if cp is not None:
        logging.info("Cached result")
        return cp
    else:
        data_provider = DataProviderService(db_engine)
        protocols_list = data_provider.get_protocols()
        data_provider.close_connection()
        if protocols_list:
                data = {"protocols": protocols_list, "total": len(protocols_list)}
                cp = jsonify(data)
                cache.set('protocol-list', cp, timeout=int(os.environ.get('timeout', 0)))
                response = make_response(cp, 200)
                response.headers["Cache-Control"] = "private"
                return response
        else:
                #
                # In case we did not find any protocols i.e the server is down
                # we send HTTP 404 - Not Found error to the client
                #
                abort(404)

@require_app_key
def get_covid_data():
    cp = cache.get('covid-protocols')
    if cp is not None:
        logging.info("Cached result")
        return cp
    else:
        data_provider = DataProviderService(db_engine)
        protocols_list = data_provider.get_covid_protocols()
        data_provider.close_connection()
        if protocols_list:
            data = {"covid-protocols": protocols_list, "total": len(protocols_list)}
            cp = jsonify(data)
            cache.set('covid-protocols', cp, timeout=int(os.environ.get('timeout', 0)))
            response = make_response(cp, 200)
            response.headers["Cache-Control"] = "private"
            return response
        else:
            #
            # In case we did not find any protocols i.e the server is down
            # we send HTTP 404 - Not Found error to the client
            #
            abort(404)

def health():
    return Response("Healthy", status=200, mimetype='application/json')
