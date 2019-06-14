# docker-python-flask-oracle-Oncore
This docker images serves as an environment to execute a OCR-API.

All the configurable variables are set up in environmental file

Your environment file must contain the following variables:

```
username=

password=

hostname=

port=

sid=

log_file=

timeout=

api_key=
```

Deploy the docker image
1. docker pull hkoranne/ocr-api
2. docker run -p 5000:5000 --env-file {your_env_file_location} -v {desired location for logs}:/opt/data/ocr_api/logs hkoranne/ocr_api:1.0

You can now access the api via https://your_oncore_url/ocr/api/protocols
