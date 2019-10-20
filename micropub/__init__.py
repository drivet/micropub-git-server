import logging
from flask import Flask
from micropub.media import media_bp
from micropub.micropub import micropub_bp


app = Flask(__name__)


app.register_blueprint(media_bp, url_prefix='/media')
app.register_blueprint(micropub_bp, url_prefix='/')
app.logger.setLevel(logging.INFO)
