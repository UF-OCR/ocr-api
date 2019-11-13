# UF's OCR API

This document provides an overview of the REST-based OCR API and its technical infrastructure, as developed and provided by Office of Clinical Research at University of Florida. This API is an extension to OnCore WSDL and SIP interfaces providing features not available in either.

Readers of this document are assumed knowledgeable in the areas of web-based technologies.
The API supports a get protocol operation that returns a list of protocol numbers and their titles available in OnCore. This functionality was created to address the need to see OnCore protocols not yet open to accrual from code. It is used in the [REDCap OnCore Client](https://github.com/ctsit/redcap_oncore_client)

## Architecture

The REST-based API employs a design based on the FLASK framework and utilizes Hypertext Transfer Protocol Secure (HTTPS) as the transport protocol. JSON is used as the data exchange format. The OCR API is a stand-alone module separate from OnCore. I can be deployed within your institutional server or on a separate Docker host. In either case, it will need access to the OnCore database.

![ocr_api_architecture](img/overview.png)

## Security

Access to any operation within the OCR API requires authentication. A token and an OnCore username are used to authenticate a request. A random sequence of characters (`api_key`) of a certain length is stored with the associated user(`api_user`) in the environment file. The api key is unique and has a one to one relation with the user. The api key has no expiration date and is verified with a string comparision. The api user is validated against OnCore's User table to verify the account access.

## Using the API

The OCR API makes the endpoint available from the registered URL.

```
• URI scheme: /api/{operation_name}
• Consumes: application/json
• Produces: application/json
• Operation name: protocols
• Headers: x-api-key(the secret key provided to the user)
           x-api-user(User name)
```

### Description:

Returns a list of protocol numbers and titles in a JSON format. Receives the header data in JSON format. Authorizes the User via token based authentication. On success, prepares a JSON object with all the protocol numbers and titles available in OnCore. This object can be cached. The cache time is configurable and is discussed in detail in the _Deployment_ section.


### Response

| Code | Description        |Schema                          |
| ---- | ------------------ | ------------------------------ |
| 200  | Protocol numbers and titles | `<Protocols>`Array  |

#### Protocols list

| Index| Description        |Schema                          |
| ---- | ------------------ | ------------------------------ |
|   0  | OnCore Protocol No.| String |
|   1  | OnCore Title.| String |

## Deployment

Docker public image is available for the OCR-API. This image serves as an environment to execute OCR-API in the server you wish.

### Prerequisites

- Docker Engine >= 1.10.0
- Docker Compose is recommended with a version 1.6.0 or later.
- Access to the OnCore database servers

### How to use this image

Run the command below to pull the image and run the OCR API on your server. In the example below, the OCR API runs on `http://localhost:5000` with the current directory as the workspace. The option of `--env-file` is used to specify the file of environmental variables used to configure the container.

    # script to run the image
    docker run -p 5000:5000 --env-file {your_env_file_location} -v {your_log_file_dir}:$log_file ufocr/ocr_api:latest

In order to run API on https connection additional proxy settings might be required. Please contact your server administrator to verify if you can create a proxy on port 5000.

### Variables
- `your_env_file_location`: the location of the environment file. This file includes all the required environmental variables.
- `your_log_file_dir`: the volume where you want to store the log files.

### Environmental variables

The following variables are required:
- Database connection variables:
    - `username`: This variable is used to provide the OnCore database user name
    - `password`: This variable is used to provide the OnCore database password
    - `hostname`: This variable is used to provide the OnCore database hostname
    - `sid`: This variable is used to provide the OnCore serviceid
- Other variables:
    - `log_file`: This variable is used to provide the log file location for the application.
    - `timeout`: This variable is used to provide the cache duration
    - `api_tokens`: This variable is used to provide the whitelisted username and their tokens in json format. Ex: {"username":"token"}

### Image variants

`/ocr_api:latest`

This image is based on the latest stable version

`ufocr/ocr_api:<version>`

This image is based on the given stable version

`ufocr/ocr_api:develop`

This image is based on the current state and is used to test out the developments before publishing


## Implementation and Maintenance

The client application is developed, tested, and maintained by the customers. See the [REDCap OnCore Client](https://github.com/ctsit/redcap_oncore_client) for an example implementation.

During OnCore upgrades, time and resources should be allocated to ensure the client applications and the OCR API workflows continue to work as expected.
