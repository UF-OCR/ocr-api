from flask import Flask, request, jsonify, render_template, Markup, session, redirect, abort
from zeep import Client, Settings, xsd
from requests import Session
from requests.auth import AuthBase, HTTPBasicAuth
from zeep.transports import Transport
import os
import sys
import datetime
import time
from classes.client import *
import logging
from middleware import log_details

logging.basicConfig(filename=os.environ.get('log_file', None), level=logging.DEBUG)

def validate_protocol(protocol_no):
    ip_address = request.remote_addr
    call_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d%H:%M:%S')
    try:
        username = request.authorization["username"]
        password = request.authorization["password"]
        client = initialize_client(username, password)
        if not client:
            log_details_id = log_details(username, ip_address, call_time,0,2);
            abort(401)
        protocol_results = protocol_info(client, protocol_no)
        log_details_id = log_details(username, ip_address, call_time, 1, 2);
        if protocol_results:
            return protocol_results
        else:
            log_details_id = log_details(username, ip_address, call_time, 0, 2);
            abort(401)
    except:
        log_details_id = log_details(username, ip_address, call_time, 0, 2);
        abort(401)

def summary_accrual():
    ip_address = request.remote_addr
    call_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d%H:%M:%S')
    try:
        data = request.get_json()
        ## all of the below are required
        username = data["credentials"]["username"]
        password = data["credentials"]["password"]
        protocol_no = data["protocol_no"]
        # proceed only if user credentials are valid
        client = initialize_client(username, password)
        if not client:
            log_details_id = log_details(username, ip_address, call_time, 0, 3);
            abort(401)
        authorized = authorize(client, protocol_no)
        if authorized == 402:
            log_details_id = log_details(username, ip_address, call_time, 1, 3);
            return jsonify({"status": authorized, "error": "Protocol no was not provided"})
        if authorized != 200:
            log_details_id = log_details(username, ip_address, call_time, 0, 3);
            return jsonify({"status": authorized, "error": "Unable to authenticate the user for the given protocol"})
        accrual_data = data["accrual_data"]
        results = process_data(client, accrual_data, protocol_no)
        log_details_id = log_details(username, ip_address, call_time, 1, 3);
        return results
    except:
        log_details_id = log_details(username, ip_address, call_time, 0, 3);
        #return sys.exc_info()
        abort(404, sys.exc_info()[1])

