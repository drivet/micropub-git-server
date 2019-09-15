import logging
import os

from flask import Flask
from micropub.media import media_bp
from micropub.micropub import micropub_bp


app = Flask(__name__)

# for Flask-IndieAuth
app.config['ME'] = os.environ['ME']
app.config['TOKEN_ENDPOINT'] = os.environ['TOKEN_ENDPOINT']

app.register_blueprint(media_bp, url_prefix='/media')
app.register_blueprint(micropub_bp, url_prefix='/')
app.logger.setLevel(logging.INFO)
