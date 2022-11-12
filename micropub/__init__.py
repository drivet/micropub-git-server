import logging
from flask import Flask
from micropub.micropub import micropub_bp


app = Flask(__name__)


app.register_blueprint(micropub_bp, url_prefix='/')
app.logger.setLevel(logging.INFO)
