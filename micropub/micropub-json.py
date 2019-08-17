import json
import requests
import os
import base64

from jsonschema import validate
from flask import Response, Blueprint
from flask import current_app as app
from flask import request
from flask import current_app
from flask_indieauth import requires_indieauth
from werkzeug.datastructures import MultiDict
from mf2schema import mf2schema


micropub_bp = Blueprint('micropub_bp', __name__)


def handle_query():
    q = request.args.get('q')
    if q == 'config' or q == 'syndicate-to':
        filename = app.config['MICROPUB_CONFIG']
        with open(filename) as f:
            return f.read()
    else:
        print('Could not file config file')
        return Response(status=400)


def make_create_request():
    """Return a decoded json object for a create request, or convert the web
    form data and return that.
    """
    json_data = request.get_json()
    if json_data:
        validate(json.loads(mf2schema), json_data)
        return json_data
    return form2json(request.form)


def form2json(form):
    result = MultiDict()
    htypes = extract_property(form, 'h')
    if htypes is None:
        result['type'] = 'h-entry'
    else:
        result['type'] = map(lambda t: 'h-' + t, htypes)
    result['properties'] = extract_object_properties(form)
    return result


def extract_object_properties(form):
    result = {}
    for k in filter(lambda k: k != 'h', map(lambda k: propname(k))):
        result[k] = extract_property(form, k)
    return result


def propname(prop):
    if prop.endswith('[]'):
        return prop[:-2]
    return prop


def extract_property(form, prop):
    mprop = prop + '[]'
    if mprop in form:
        return form.getlist(mprop)
    elif prop in form:
        return [form[prop]]
    else:
        return None


def handle_create():
    request_data = make_create_request()
    permalink = make_permalink(request_data)
    save_post(request_data)
    resp = Response(status=202)
    resp.headers['Location'] = permalink
    return resp


def save_post(request_data):
    pass


def make_permalink(request_data):
    pass


def b64(s):
    return base64.b64encode(s.encode()).decode()


def commit_file(url, content):
    return requests.put(url, auth=(os.environ['USERNAME'],
                                   os.environ['PASSWORD']),
                        data=json.dumps({'message': 'post to ' + url,
                                         'content': b64(content)}))


@micropub_bp.route('/', methods=['GET', 'POST'], strict_slashes=False)
@requires_indieauth
def handle_root():
    if request.method == 'GET':
        if 'q' in request.args:
            return handle_query()
        else:
            app.logger('GET only works for queries')
            return Response(status=400)
    elif request.method == 'POST':
        if 'action' in request.form:
            app.logger.error('Actions other than create not supported')
            return Response(status=400)
        else:
            return handle_create()
    else:
        app.logger.error('HTTP method not supported: ' +
                                 request.method)
        return Response(status=403)
