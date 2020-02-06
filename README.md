# UF's OCR API

This document provides an overview of the REST-based OCR API and its technical infrastructure, as developed and provided by Office of Clinical Research at University of Florida. Readers of this document are assumed knowledgeable in the areas of web-based technologies.
The API supports a get protocol operation that returns a list of protocol#s and their titles available in OnCore.

## Architecture
The REST-based API employs a design based on FLASK framework and utilizes Hypertext Transfer Protocol Secure (HTTPS) as the transport protocol. JSON is used as the data exchange format to ensure the communications. The OCR API is a stand-alone module and is deployed within your institutional server which has access to the OnCore database's.

![ocr_api_architecture](img/overview.png)

## Security

Access to any operation within the OCR API requires authentication. A token, and an OnCore username is used to authenticate a request. A random sequence of character(api_key) of a certain length is stored with the associated user(api_user) in the environment file. The api key is unique and has a one to one relation with the user. The api key has no expiration date and is verified with a string comparision. The api user is validated against OnCore's User table to verify the account access.

## Using the API
The OCR API makes available the endpoint for the registered URL.

```
• URI scheme: /api/{operation_name}
• Available operations: protocols, accruals and validateProtocol
```
## Operations

### Protocols
```
GET /protocols
Produces: application/json
```

#### Description

Returns a list of protocol no, and title in a JSON format. Receives the header data in JSON format. Authorizes the User via token based authentication. On success, prepares a JSON object with all the protocol # and titles available in OnCore. This object can be cached. The cache time is configurable and is discussed in detail under deployment session.

#### Response

| Code | Description        |Schema                          |
| ---- | ------------------ | ------------------------------ |
| 200  | Protocol #'s, and titles | `<Protocols>`Array  |

##### Protocols list

| Index| Description        |Schema                          |
| ---- | ------------------ | ------------------------------ |
|   0  | OnCore Protocol No.| String |
|   1  | OnCore Title.| String |

### validateProtocol
```
GET /validateProtocol/<protocol_no>
Produces: boolean
```
#### Description
Validates if the protocol is eligible to record the summary accruals data. This summary accrual import process
only applies to studies that are eligible to record summary data (see Study Eligibility below).

##### Study Eligibility:
- The protocol’s SummaryAccrualInfo field should be set to ‘Y’

#### Response
| HTTP CODE               |Description                     |Schema      |
| ------------------ | ------------------------------ |------------|
| 200 | The protocol results provided| protocolDetails |

#### protocolDetails
| Name              |Description                     |Schema      |
| ------------------ | ------------------------------ |------------|
| protocol_no | The OCR protocol #  | string |
| title | Title of the protocol|string|
| accrual_info_only| open for summary accruals| boolean|

### accruals
```
POST /accruals
Consumes: application/json
Produces: application/json
```

#### Description:

Receives the accrual data, protocol no, and OnCore user credentials in JSON format. Authorizes the User via
OnCore SOAP API. On success, transforms accrual data into summary accrual import format and imports the data
into OnCore via SOAP API. Returns a protocol no, # of accruals successfully imported, # of accruals failed to import
and a list of transaction messages for each summary accrual data sent in a JSON format.

#### Parameters
| Name               |Description                     |Schema      |
| ------------------ | ------------------------------ |------------|
| Credentials* | OnCore username and password used for authentication|Credentials |
| Protocol No* | UF Protocol No.(UF OCR#) | string|
| Accrual Data* | Accrual records of the Protocol | <AccrualData> array|

#### Credentials
| Name               |Description                     |Schema      |
| ------------------ | ------------------------------ |------------|
| Username* | OnCore username| string |
| Password* | OnCore password| string|

#### AccrualData
| Name               |Description                     |Schema      |
| ------------------ | ------------------------------ |------------|
| On Study Date* | On study date of the accrual| datetime |
| Institution | Recruited institution of the accrual. Defaulted to “University of Florida”| string|
| Gender | OnCore Gender mapped value| string|
| Date of Birth| DOB of the accrual| datetime|
| Age at enrollment| Age of the accrual| integer
|Ethnicity| OnCore ethnicity mapped value| string
|Race| OnCore race mapped value| string
|Disease Site| OnCore disease site mapped value| string
|First Name| Recruited Staff First Name|string
|Last Name| Recruited Staff Last Name|string
|Email Address| Recruited Staff Email Address|string
|ZipCode| Accruals recruited zipcode|integer

#### Response
| HTTP CODE               |Description                     |Schema      |
| ------------------ | ------------------------------ |------------|
| 200 | Import details for the protocol provided| accrualImportDetails |

#### AccrualImportDetails
| Name              |Description                     |Schema      |
| ------------------ | ------------------------------ |------------|
| protocol_no | The protocol # of the accrual data | string |
| success_records | # of accrual data successfully imported| <TransactionMessages>array|
| error_records| # of accrual data failed to import| <TransactionMessages>array|
| total_accruals| # of successful accruals| integer|

#### TransactionMessages
| Name              |Description                     |Schema      |
| ------------------ | ------------------------------ |------------|
| from_date | The first date of the month of on study date | string |
| thru_date | The last date of the month of on study date | string |
|institution|Recruited at institution|string
|internal_accrual_reporting_group|Type of accrual reporting group|string
|gender|Gender value|string
|age_group|Range of age|string
|ethnicity|Ethnicity value|string
|race|Race value|string
|disease_site|Disease site value|string
|recruited_by|Recruited by staff|JSON
|zip_code|Recruited at zipcode|integer
|accrual|Total # of accruals|integer
|message|Message received from SOAP API|string

#### recruited_by
| Name              |Description                     |Schema      |
| ------------------ | ------------------------------ |------------|
|first_name|The first name of the recruited staff|string
|last_name|The last name of the recruited staff|string
|middle_name|The middle name of the recruited staff|string

## Deployment

Docker public image is available for the OCR-API. This image serves as an environment to execute OCR-API in the server you wish.

### Prerequisites

- Docker Engine >= 1.10.0
- Docker Compose is recommended with a version 1.6.0 or later.
- Access to the OnCore database servers

### How to use this image
Run the below command to pull the image and run OCR API on your server. THE OCR API runs on http://localhost:5000 with the current directory as our workspace. The option of --env-file is added to provide the configured environmental variable's.

    # script to run the image
    docker run -p 5000:5000 --env-file {your_env_file_location} -v {your_log_file_dir}:$log_file ufocr/ocr_api:latest

In order to run API on https connection additional proxy settings might be required. Please contact your server administrator to verify if you can create a proxy on port 5000.

### Variables
- your_env_file_location: the location of the environment file. This file includes all the required environmental variables
- your_log_file_dir: the location to the folder where you desire to volume the log files

### Environmental variables

The following variables and required:
- Database connection variables:
    - username: This variable is used to provide the OnCore database user name
    - password: This variable is used to provide the OnCore database password
    - hostname: This variable is used to provide the OnCore database hostname
    - sid: This variable is used to provide the OnCore serviceid
- Other variables:
    - log_file: This variable is used to provide the log file location for the application.
    - timeout: This variable is used to provide the cache duration
    - api_tokens: This variable is used to provide the whitelisted username and their tokens in json format. Ex: {"username":"token"}

### Image variants

`/ocr_api:latest`

This image is based on the latest stable version

`ufocr/ocr_api:<version>`

This image is based on the given stable version

`ufocr/ocr_api:develop`

This image is based on the current state and is used to test out the developments before publishing


## Implementation and Maintenance
The client application is developed, tested, and maintained by the customers. During OnCore upgrades time and resources need to be allocated to ensure the client applications and the OCR API workflows continue to work as expected.
