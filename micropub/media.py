import uuid
import os
import errno
import datetime

from PIL import Image
from flask import Response, request, Blueprint, send_from_directory, url_for
from flask import current_app as app
from flask_indieauth import requires_indieauth
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'PNG', 'JPG', 'JPEG',
                          'GIF'])
IMAGE_SIZE = 1024

media_bp = Blueprint('media_bp', __name__)


@media_bp.route('/<path:imagepath>', methods=['GET'], strict_slashes=False)
def handle_get(imagepath):
    app.logger.info('Handling media GET with ' + imagepath)
    return send_from_directory(app.config['UPLOAD_FOLDER'], imagepath)


@media_bp.route('/', methods=['POST'], strict_slashes=False)
@requires_indieauth
def handle_post():
    app.logger.info('Handling media POST')
    # check if the post request has the file part
    if 'file' not in request.files:
        return Response(response='no file part', status=400)
    file = request.files['file']

    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return Response(response='no selected file', status=400)

    if file and allowed_file(file.filename):
        image_file = create_filename(secure_filename(file.filename))
        image_folder = make_image_folder()

        save_image(file, image_folder, image_file)
        outfile = resize_image(image_folder, image_file)
        location = app.config['HOST'] + \
            url_for('media_bp.handle_get', imagepath=outfile)
        app.logger.info(f'Sending back location {location}')

        resp = Response(status=201)
        resp.headers['Location'] = location
        return resp
    else:
        return Response(response='File isn\'t among allowed types', status=400)


def make_image_folder():
    now = datetime.datetime.now()
    year = str(now.year)
    month = now.month
    return os.path.join(year, f'{month:02d}')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_filename(filename):
    base, ext = os.path.splitext(filename)
    return str(random()) + ext


def random():
    return uuid.uuid4()


def save_image(file, image_folder, image_file):
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_folder)
    ensure_folder(image_path)
    abs_image_path = os.path.join(image_path, image_file)
    app.logger.info(f'saving {abs_image_path}')
    file.save(abs_image_path)


def ensure_folder(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def resize_image(image_folder, image_file):
    infile = os.path.join(image_folder, image_file)
    outfile = os.path.join(image_folder, '0_' + image_file)
    try:
        upload_folder = app.config['UPLOAD_FOLDER']
        im = Image.open(os.path.join(upload_folder, infile))
        im.thumbnail((IMAGE_SIZE, IMAGE_SIZE), Image.ANTIALIAS)
        im.save(os.path.join(upload_folder, outfile), "JPEG")
        return outfile
    except IOError:
        app.logger.error("cannot create thumbnail for '%s'" % infile)
