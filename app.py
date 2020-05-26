from flask import Flask
from routes import init_api_routes

app = Flask(__name__)
init_api_routes(app)

@app.errorhandler(500)
def handle_500(error):
    return str(error), 500

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')


