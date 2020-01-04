from flask import Flask
from flask_cors import *
from config import  DevConfig

from controllers.warehouse import wh_blueprint

app = Flask(__name__)
app.secret_key = 'very hard code'
CORS(app, support_credentials=True, max_age=3600)

app.config.from_object(DevConfig)

app.register_blueprint(wh_blueprint)

if __name__ == '__main__':
    app.run()
