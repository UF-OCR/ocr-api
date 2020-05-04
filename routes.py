from middleware import get_ocr_protocols, get_covid_data
from soap_client import validate_protocol, summary_accrual

def init_api_routes(app):
    if app:
         app.add_url_rule('/api/protocols', 'get_ocr_protocols', get_ocr_protocols, methods=['GET'])
         app.add_url_rule('/api/covid', 'get_covid_data', get_covid_data, methods=['GET'])
         app.add_url_rule('/api/oncore/validateProtocol/<protocol_no>', 'validate_protocol', validate_protocol, methods=['GET'])
         app.add_url_rule('/api/oncore/accruals', 'summary_accrual', summary_accrual, methods=['POST'])