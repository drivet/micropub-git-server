import os

from flask import Flask
from micropub.media import media_bp
from micropub.micropub_json import micropub_bp


def get_root():
    if 'MICROPUB_ROOT' in os.environ:
        return os.environ['MICROPUB_ROOT']
    else:
        my_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(my_path, '../run')


root = get_root()
app = Flask(__name__)
app.config.from_json(root + '/settings.json')
app.config['UPLOAD_FOLDER'] = root + '/upload_folder'
app.config['MICROPUB_CONFIG'] = root + '/config.json'
app.register_blueprint(media_bp, url_prefix='/media')
app.register_blueprint(micropub_bp, url_prefix='/')
