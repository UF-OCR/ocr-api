from middleware import get_ocr_protocols

def init_api_routes(app):
    if app:
         app.add_url_rule('/api/protocols', 'get_ocr_protocols', get_ocr_protocols, methods=['GET'])