from flask import jsonify
from zeep import Client, Settings, xsd
from requests import Session
from requests.auth import AuthBase, HTTPBasicAuth
from zeep.transports import Transport
import os
import pickle
import pandas as pd
import numpy as np
import json

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

def protocol_info(client, protocol_no):
        if client:
                with client.settings(strict=False, raw_response=False):
                        response = client.service.getProtocol(protocolNo=protocol_no, irbNo=xsd.SkipValue)
                        if response:
                                response_json = {"protocol_no": response[0]['ProtocolNo'], "title": response[0]['Title'],
                                                 "accrual_info_only": response[0]['SummaryAccrualInfoOnly'] == 'Y'}
                        else:
                                response_json = {"protocol_no": protocol_no,
                                                 "error": "Invalid OCR#"}
                        return jsonify(response_json)
        else:
                return None

def authorize(client, protocol_no):
    try:
        if client:
                with client.settings(raw_response=True):
                        if protocol_no:
                                response = client.service.deleteSummaryAccrualInfo(ProtocolNo=protocol_no, FromDate=xsd.SkipValue,
                                                                                       ThruDate=xsd.SkipValue, InternalAccrualReportingGroup=xsd.SkipValue, deleteAll=True)
                                if response:
                                        return response.status_code
                                else:
                                        return 401
                        else:
                                return 402
    except:
        return 401

def process_data(client, accrual_data, protocol_no):
        data = pd.DataFrame(data=accrual_data)
        data.columns = map(str.lower, data.columns)

        if "id" not in data:
                data["id"] = data.index + 1

        if 'on study date*' not in data:
                return None, None, 0, None

        # identify the empty on study rows
        empty_onstudydate_rows = data[data['on study date*'] == ""].index

        if len(empty_onstudydate_rows) > 0:
                empty_onstudydate_records = data.loc[empty_onstudydate_rows,['id']].to_dict("records")
        else:
                empty_onstudydate_records = None

        data['on study date*'] = pd.to_datetime(data['on study date*'])

        if 'date of birth' not in data:
                data['date of birth'] = ""
                if 'age at enrollment' in data:
                        data['age at enrollment'] = data['age at enrollment'].fillna(0)
        else:
                data['date of birth'] = pd.to_datetime(data['date of birth'])
                data['date of birth'] = data['date of birth'].where(data['date of birth'] <= data['on study date*'],
                                                                    data['date of birth'] - np.timedelta64(100, 'Y'))  # 2
                ageAtEnrollment = (data['on study date*'] - data['date of birth']).astype('<m8[Y]')  # 3
                data['age at enrollment'] = ageAtEnrollment

        invalid_age_records = None
        # identify out of range ages
        if 'age at enrollment' in data:
                age_range_exp = os.environ.get('age_range', None)
                data['age at enrollment'] = data['age at enrollment'].astype(str)
                data['age at enrollment'] = data['age at enrollment'].str.replace(r'[-+]?\.[0-9]*','')
                data['age at enrollment'] = data['age at enrollment'].replace("",np.nan)
                invalid_age_rows = data[data['age at enrollment'].str.contains(str(age_range_exp), na=True, regex=True)==False].index
                if len(invalid_age_rows) > 0:
                        invalid_age_records = data.loc[invalid_age_rows,['id']].to_dict("records")
                        empty_onstudydate_rows = empty_onstudydate_rows.union(invalid_age_rows)
        # drop data
        data = data.drop(empty_onstudydate_rows)

        if len(data) <= 0:
                return jsonify({"total_accruals": 0, "protocol_no": protocol_no, "error_records": None,
                                "success_records": None, "invalid_onstudy_rows": empty_onstudydate_records,
                                "invalid_age_rows": invalid_age_records})

        if 'age at enrollment' in data:
                numeric_rows = data[data['age at enrollment'].str.contains(str(age_range_exp), na=False, regex=True)].index
                ageAtEnrollment = data.loc[numeric_rows,['age at enrollment']]
                rangeStart = ageAtEnrollment.astype(int) // 10 * 10
                rangeEnd = (ageAtEnrollment.astype(int) // 10 * 10) + 9
        else:
                rangeStart = ""
                rangeEnd = ""

        # add through and from range
        data['start range'] = rangeStart
        data['end range'] = rangeEnd
        data['thru date'] = data['on study date*'] + pd.offsets.MonthEnd(0)
        data['from date'] = data['thru date'] + pd.offsets.MonthBegin(-1)
        data['thru date'] = data['thru date'].dt.strftime('%Y-%m-%d')
        data['from date'] = data['from date'].dt.strftime('%Y-%m-%d')
        data['thru date'] = data['thru date'].fillna("")
        data['from date'] = data['from date'].fillna("")

        if 'email address' not in data:
                data['email address'] = ''

        if 'gender' not in data:
                data['gender'] = ''

        if 'ethnicity' not in data:
                data['ethnicity'] = ''

        if 'race' not in data:
                data['race'] = ''

        if 'disease site' not in data:
                data['disease site'] = ''

        if 'institution' not in data:
                data['institution'] = ''

        data['institution'] = data['institution'].apply(lambda x: "University of Florida" if isinstance(x, str) and (x.isspace() or not x) else x)

        data['internal accrual reporting group'] = data['institution']

        iMap = {'University of Florida': 'Research Center',
                'Malcom Randall VA Medical Center': 'Veterans Administration'}

        data['internal accrual reporting group'] = data['internal accrual reporting group'].map(iMap)

        data['internal accrual reporting group'] = data['internal accrual reporting group'].fillna("Affiliate")

        if 'first name' not in data:
                data['first name'] = ''
                data['last name'] = ''
                data['email address'] = ''

        if 'zip code' not in data:
                data['zip code'] = ''

        data = data.fillna("")

        data = data.drop(columns=["date of birth"])

        group_columns = ['from date', 'thru date', 'institution', 'internal accrual reporting group', 'gender',
                         'start range','end range', 'ethnicity', 'race', 'disease site', 'first name', 'last name', 'email address',
                         'zip code']

        grouped_data_count = data.groupby(group_columns)['id'].count()
        grouped_data = data.groupby(group_columns)['id'].agg(lambda x: x.tolist())
        content = grouped_data_count.to_dict()
        success = []
        error = []
        total_summary_accurals = 0
        oncore_code_mappings = pickle.load(open('oncore_code_mappings.p', 'rb'))

        for key, value in content.items():
                id= grouped_data[key]
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
                accrual = value
                key.append(accrual)
                staffDict = {}
                personTypeDict = {}
                personTypeDict["FirstName"] = key[10]
                personTypeDict["MiddleName"] = ""
                personTypeDict["LastName"] = key[11]
                zipCode = key[13]
                staffDict["Name"] = personTypeDict
                staffDict["Institution"] = "University of Florida"
                json_response = {"id": id, "from_date": fromDate, "thru_date": thruDate, "instituition": instituition,
                                 "internal_accrual_reporting_group": internalAccrualReportingGroup,
                                 "gender": gender, "age_group": ageGroup, "ethnicity": ethnicity, "race": race,
                                 "disease_site": diseaseSite, "recruited_by": personTypeDict, "zip_code": zipCode,
                                 "accrual": accrual}
                if client:
                        with client.settings(raw_response=False):
                                response = client.service.saveSummaryAccrualInfo(ProtocolNo=protocol_no, FromDate=fromDate,
                                                                                 ThruDate=thruDate, DiseaseSite=diseaseSite,
                                                                                 Diagnosis=xsd.SkipValue,
                                                                                 InternalAccrualReportingGroup=internalAccrualReportingGroup,
                                                                                 AgeGroup=ageGroup, Institution=instituition,
                                                                                 Gender=gender, Ethnicity=ethnicity,
                                                                                 Race=race, RecruitedBy=staffDict, ZipCode=zipCode,
                                                                                 Accrual=accrual)
                                if response['message'] is not None:
                                        json_response["soap_message"] = response['message']
                                        total_summary_accurals += key[14]
                                        success.append(json_response)

                                if response['error'] is not None:
                                        json_response["soap_message"] = response['error']
                                        error.append(json_response)

        return jsonify({"total_accruals": total_summary_accurals,"protocol_no":protocol_no,"error_records": error,"success_records": success,"invalid_onstudy_rows": empty_onstudydate_records, "invalid_age_rows": invalid_age_records})

def map_codes(oncore_code_mappings, field, value):
    # If provided data is a coded value for its respective field,
    # convert it to the description string, otherwise provide the raw value
    try:
        return oncore_code_mappings[field][str(value)]
    except KeyError:
        return value
