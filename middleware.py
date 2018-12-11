from flask import jsonify
import pandas as pd
from functools import wraps
from flask import request, abort
from werkzeug.contrib.cache import SimpleCache
import logging
import ConfigParser
from data_provider_service import engine

config = ConfigParser.RawConfigParser()
config.read('config.properties')

logging.basicConfig(filename=config.get('Default', 'log_file'), level=logging.DEBUG)

cache = SimpleCache()


# The actual decorator function
def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        with open('api.key', 'r') as apikey:
            key = apikey.read().replace('\n', '')
            logging.info("Validating key " + request.headers.get('x-api-key'))
        # if request.args.get('key') and request.args.get('key') == key:
        if request.headers.get('x-api-key') and request.headers.get('x-api-key') == key:
            logging.info("Validated")
            return view_function(*args, **kwargs)
        else:
            logging.info("Validation failed")
            abort(401)

    return decorated_function


@require_appkey
def get_ocr_protocols():
    cp = cache.get('protocol-list')
    if cp is not None:
        logging.info("Cached result")
        return cp
    else:
        df = pd.read_sql('SELECT distinct protocol_no FROM oncore.sv_pcl_details', engine)
        logging.info("Total protocols %s", len(df.index))
        if df.to_json(orient='values'):
            cp = jsonify({"protocols": df.to_json(orient='values')})
            cache.set('protocol-list', cp, timeout=config.getfloat('Default', 'timeout'))
            return cp
        else:
            #
            # In case we did not find any protocols i.e the server is down
            # we send HTTP 404 - Not Found error to the client
            #
            abort(404)
