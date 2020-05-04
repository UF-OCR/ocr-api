from flask import jsonify
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

oracle_connection_string = 'oracle+cx_oracle://{username}:{password}@{hostname}:{port}/{sid}'

db_engine = oracle_connection_string.format(
    username=os.environ.get('username', None),
    password=os.environ.get('password', None),
    hostname=os.environ.get('hostname', None),
    port=os.environ.get('port', 0),
    sid=os.environ.get('sid', None)
)



def log_details(username, ip_address, call_time, validated,op_type):
    DATA_PROVIDER = DataProviderService(db_engine)
    log_details_id = DATA_PROVIDER.log_details(username, ip_address, call_time, validated, op_type)
    DATA_PROVIDER.close_connection()
    return log_details_id

def require_app_key(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        logTable = os.environ.get('log_functionality', False)
        tokens = os.environ.get('api_tokens', None)
        tokens = json.loads(tokens)
        username = request.headers.get('x-api-user')
        key = request.headers.get('x-api-key')
        password = None
        if username in tokens:
            password = tokens[username]
        ip_address = request.remote_addr
        call_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d%H:%M:%S')
        logging.info("Validating key " + str(key))
        if ip_address and key and password and key == password and username and tokens[username]:
            logging.info("Validated")
            validated = 1
            if logTable:
                new_log_details_id = log_details(username, ip_address, call_time, validated,1)
            else:
                new_log_details_id = ip_address
            if new_log_details_id:
                logging.info("Logged with"+str(new_log_details_id))
                return view_function(*args, **kwargs)
            else:
                #
                # In case we could not log the server is down
                # we send HTTP 404 - Not Found error to the client
                #
                logging.info("failed Logging")
                abort(404)
        else:
            validated = 0
            if logTable:
                new_log_details_id = log_details(username, ip_address, call_time, validated,1)
            else:
                new_log_details_id = ip_address
            if new_log_details_id:
                logging.info("Logged with"+str(new_log_details_id))
            else:
                logging.info("failed logging with"+str(new_log_details_id))
            abort(401)

    return decorated_function


@require_app_key
def get_ocr_protocols():
    DATA_PROVIDER = DataProviderService(db_engine)
    cp = cache.get('protocol-list')
    if cp is not None:
        logging.info("Cached result")
        return cp
    else:
        protocols_list = DATA_PROVIDER.get_protocols()
        if protocols_list:
            data = {"protocols": protocols_list, "total": len(protocols_list)}
            cp = jsonify(data)
            cache.set('protocol-list', cp, timeout=int(os.environ.get('timeout', 0)))
            DATA_PROVIDER.close_connection()
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
        DATA_PROVIDER = DataProviderService(db_engine)
        protocols_list = DATA_PROVIDER.get_covid_protocols()
        DATA_PROVIDER.close_connection()
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