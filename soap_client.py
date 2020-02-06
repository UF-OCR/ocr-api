from flask import Flask, request, jsonify, render_template, Markup, session, redirect, abort
import pandas as pd
import numpy as np
from zeep import Client, Settings, xsd
from requests import Session
from requests.auth import AuthBase, HTTPBasicAuth
from zeep.transports import Transport
import os
import sys
from datetime import timedelta
from classes.client import initialize_client
import json
import pickle

def validate_protocol(protocol_no):
    try:
        username = request.authorization["username"]
        password = request.authorization["password"]
        client = initialize_client(username, password)
        if client:
            with client.settings(strict=False, raw_response=False):
                response = client.service.getProtocol(protocolNo=protocol_no, irbNo=xsd.SkipValue)
                response_json = {"protocol_no":response[0]['ProtocolNo'], "title":response[0]['Title'], "accrual_info_only":response[0]['SummaryAccrualInfoOnly']=='Y'}
                return jsonify(response_json)
        return None
    except:
        abort(404,"Username/password is incorrect")

def summary_accrual():
    try:
        data = request.get_json()
        username = data["credentials"]["username"]
        password = data["credentials"]["password"]
        protocol_no = data["protocol_no"]
        accrual_data = data["accrual_data"]
        if isinstance(accrual_data, list):
            if accrual_data is not None and len(accrual_data)==0:
                return str("No accrual data received")
        if not isinstance(accrual_data, (list)):
            if accrual_data is None or accrual_data=="":
                return str("No accrual data received")
            accrual_data = json.loads(accrual_data)
        data = pd.DataFrame(data=accrual_data)

        if 'Date of Birth' not in data:
            data['Date of Birth'] = ''
            if 'Age at Enrollment' in data:
                data['Age at Enrollment'] = data['Age at Enrollment'].fillna(0)
                ageAtEnrollment = pd.to_numeric(data['Age at Enrollment'])
            else:
                ageAtEnrollment = 0
        else:
            data['Date of Birth'] = data['Date of Birth'].fillna("")
            now = pd.Timestamp('now')
            data['Date of Birth'] = pd.to_datetime(data['Date of Birth'])
            data['Date of Birth'] = data['Date of Birth'].where(data['Date of Birth'] < now,
                                                                data['Date of Birth'] - np.timedelta64(100, 'Y'))  # 2
            ageAtEnrollment = (now - data['Date of Birth']).astype('<m8[Y]')  # 3
            data['Age at Enrollment'] = ageAtEnrollment

        rangeStart = ageAtEnrollment // 10 * 10
        rangeEnd = (ageAtEnrollment // 10 * 10) + 9

        data['Start range'] = rangeStart
        data['End range'] = rangeEnd
        data['On Study Date*'] = pd.to_datetime(data['On Study Date*'])  # 1
        data['thru Date'] = data['On Study Date*'] + pd.offsets.MonthEnd(0)
        data['from Date'] = data['thru Date'] + pd.offsets.MonthBegin(-1)
        data['thru Date'] = data['thru Date'].dt.strftime('%Y-%m-%d')
        data['from Date'] = data['from Date'].dt.strftime('%Y-%m-%d')
        data['thru Date'] = data['thru Date'].fillna("")
        data['from Date'] = data['from Date'].fillna("")

        if 'Gender' not in data:
            data['Gender'] = ''

        if 'Ethnicity' not in data:
            data['Ethnicity'] = ''

        if 'Race' not in data:
            data['Race'] = ''

        if 'Disease Site' not in data:
            data['Disease Site'] = ''

        if 'Institution' not in data:
            data['Institution'] = ''
        data['Institution'] = data['Institution'].apply(lambda x: "University of Florida" if isinstance(x, str) and (x.isspace() or not x) else x)

        data['Internal Accrual Reporting Group'] = data['Institution']
        iMap = {'University of Florida': 'Research Center',
                'Malcom Randall VA Medical Center': 'Veterans Administration'}
        data['Internal Accrual Reporting Group'] = data['Internal Accrual Reporting Group'].map(iMap)
        data['Internal Accrual Reporting Group'] = data['Internal Accrual Reporting Group'].fillna("Affiliate")

        if 'First Name' not in data:
            data['First Name'] = ''
            data['Last Name'] = ''
            data['Email Address'] = ''

        if 'Zip Code' not in data:
            data['Zip Code'] = ''

        data = data.fillna("")


        grouped_data = data.groupby(['from Date', 'thru Date', 'Institution', 'Internal Accrual Reporting Group', 'Gender', 'Start range',
                 'End range', 'Ethnicity', 'Race', 'Disease Site', 'First Name', 'Last Name', 'Email Address',
                 'Zip Code']).count()

        client = initialize_client(username, password)
        if client:
            with client.settings(raw_response=True):
                response = client.service.deleteSummaryAccrualInfo(ProtocolNo=protocol_no, FromDate=xsd.SkipValue,ThruDate=xsd.SkipValue,InternalAccrualReportingGroup=xsd.SkipValue, deleteAll=True)
                if response.status_code == 401 or response.status_code == 500:
                    return jsonify({"status":response.status_code, "error":"User not authorized for accrual updates on "+protocol_no})
        content = grouped_data.to_dict(orient="index")
        success = []
        error = []
        total_summary_accurals = 0
        oncore_code_mappings = pickle.load(open('oncore_code_mappings.p', 'rb'))
        for key, value in content.items():
            key = list(key)
            fromDate = key[0]
            thruDate = key[1]
            instituition = key[2]
            internalAccrualReportingGroup = key[3]
            gender = key[4]
            ageGroup = ""
            if key[5] is not None and key[5]!="":
                ageGroup = str(int(key[5])) + " - " + str(int(key[6]))
            ethnicity = map_codes(oncore_code_mappings, 'ethnicity', key[7])
            race = map_codes(oncore_code_mappings, 'race', key[8])
            diseaseSite = map_codes(oncore_code_mappings, 'disease_site', key[9])
            accrual = value['On Study Date*']
            key.append(accrual)
            staffDict = {}
            personTypeDict = {}
            personTypeDict["FirstName"] = key[10]
            personTypeDict["MiddleName"] = ""
            personTypeDict["LastName"] = key[11]
            zipCode = key[13]
            staffDict["Name"] = personTypeDict
            staffDict["Institution"] = "University of Florida"
            with client.settings(raw_response=False):
                try:
                    response = client.service.saveSummaryAccrualInfo(ProtocolNo=protocol_no, FromDate=fromDate,
                                                                     ThruDate=thruDate, DiseaseSite=diseaseSite,
                                                                     Diagnosis=xsd.SkipValue,
                                                                     InternalAccrualReportingGroup=internalAccrualReportingGroup,
                                                                     AgeGroup=ageGroup, Institution=instituition,
                                                                     Gender=gender, Ethnicity=ethnicity,
                                                                     Race=race, RecruitedBy=staffDict, ZipCode=zipCode,
                                                                     Accrual=accrual)
                    json_response = {"from_date": fromDate, "thru_date": thruDate, "instituition": instituition,
                                     "internal_accrual_reporting_group": internalAccrualReportingGroup,
                                     "gender": gender, "age_group": ageGroup, "ethnicity": ethnicity, "race": race,
                                     "disease_site": diseaseSite, "recruited_by": personTypeDict, "zip_code": zipCode,
                                     "accrual": accrual}
                except:
                    abort(400, "User not authorized")

                if response['message'] is not None:
                    json_response["soap_message"] = response['message']
                    total_summary_accurals += key[14]
                    success.append(json_response)

                if response['error'] is not None:
                    json_response["soap_message"] = response['error']
                    error.append(json_response)

        return jsonify({"total_accruals": total_summary_accurals,"protocol_no":protocol_no,"error_records": error,"success_records": success})
    except:
        abort(404, sys.exc_info()[1])

def map_codes(oncore_code_mappings, field, value):
    # If provided data is a coded value for its respective field, 
    # convert it to the description string, otherwise provide the raw value
    try:
        return oncore_code_mappings[field][str(value)]
    except KeyError:
        return value
