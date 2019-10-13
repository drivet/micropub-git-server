import json
import requests
import base64
import datetime
import copy
import os

from jsonschema import validate
from flask import Response, Blueprint
from flask import current_app as app
from flask import request
from flask_indieauth import requires_indieauth
from micropub.mf2schema import mf2schema
from micropub.utils import disable_if_testing, get_root

DEFAULT_CONFIG = '''{{
    "syndicate-to": [],
    "media-endpoint": "{host}/media"
}}
'''

micropub_bp = Blueprint('micropub_bp', __name__)


@micropub_bp.route('/', methods=['GET', 'POST'], strict_slashes=False)
@disable_if_testing(requires_indieauth)
def handle_root():
    if request.method == 'GET':
        if 'q' in request.args:
            return handle_query()
        else:
            app.logger.error('GET only works for queries')
            return Response(status=400)
    elif request.method == 'POST':
        app.logger.info('handling micropub root POST')
        if 'action' in request.form:
            app.logger.error('Actions other than create not supported')
            return Response(status=400)
        else:
            return handle_create()
    else:
        app.logger.error('HTTP method not supported: ' + request.method)
        return Response(status=405)


def handle_query():
    q = request.args.get('q')
    if q == 'config' or q == 'syndicate-to':
        filename = config_file()
        try:
            with open(filename) as f:
                return f.read()
        except (FileNotFoundError, IOError):
            app.logger.info(f'Could not open {filename}, ' +
                            'sending default config')
            host = os.environ['HOST']
            return DEFAULT_CONFIG.format(host=host)
    else:
        app.logger.error(f'Unsupported q value: {q}')
        return Response(status=400)


def config_file():
    return get_root() + '/config.json'


def extract_create_request(json_data, form_data):
    """Return a decoded json object for a create request, or convert the web
    form data and return that.
    """
    if json_data:
        validate(json_data, json.loads(mf2schema))
        request_data = copy.deepcopy(json_data)
    else:
        request_data = form2json(form_data)
    fill_defaults(request_data)
    return request_data


def form2json(form):
    result = {}
    htypes = extract_property(form, 'h')
    if htypes is None:
        result['type'] = ['h-entry']
    else:
        result['type'] = list(map(lambda t: 'h-' + t, htypes))
    result['properties'] = extract_object_properties(form)
    return result


def extract_object_properties(form):
    result = {}
    for k in filter(lambda k: k != 'h', map(lambda k: propname(k), form)):
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


def fill_defaults(request_data):
    date = datetime.datetime.now()
    if 'published' not in request_data['properties']:
        request_data['properties']['published'] = [date.isoformat()]


def handle_create():
    request_data = extract_create_request(request.get_json(), request.form)
    permalink = make_permalink(request_data)

    # access token is passed along with the rest of the data,
    # we don't want to save that
    props = request_data['properties']
    if 'access_token' in props:
        del props['access_token']

    save_post(request_data)
    resp = Response(status=202)
    resp.headers['Location'] = permalink
    return resp


def save_post(request_data):
    props = request_data['properties']
    published_date = get_published_date(props)
    slug = get_slug(props)
    repo_path = get_repo_path_format().format(published=published_date,
                                              slug=slug)
    url = get_repo_api_root() + repo_path
    r = commit_file(url, json.dumps(request_data))
    if r.status_code != 201:
        raise Exception('failed to post to github: ' + url)


def get_repo_api_root():
    repo = os.environ['GITHUB_REPO']
    return f'https://api.github.com/repos/{repo}/contents'


def get_repo_path_format():
    default = '/content/micropub/' + \
              '{published:%Y}/{published:%m}/{published:%d}/' + \
              '{published:%H}{published:%M}{published:%S}.mp'
    return os.environ.get('REPO_PATH_FORMAT', default)


def make_permalink(request_data):
    props = request_data['properties']
    published_date = get_published_date(props)
    slug = get_slug(props)
    return get_permalink_format().format(published=published_date, slug=slug)


def get_permalink_format():
    default = '{published:%Y}/{published:%m}/{published:%d}/{slug}'
    return os.environ.get('PERMALINK_FORMAT', default)


def get_slug(props):
    return props.get('mp-slug', [get_default_slug(props)])[0]


def get_default_slug(props):
    date = get_published_date(props)
    return '{published:%H}{published:%M}{published:%S}'.format(published=date)


def get_published_date(props):
    return datetime.datetime.strptime(props['published'][0],
                                      '%Y-%m-%dT%H:%M:%S.%f')


def commit_file(url, content):
    c = base64.b64encode(content.encode()).decode()
    return requests.put(url, auth=(os.environ['GITHUB_USERNAME'],
                                   os.environ['GITHUB_PASSWORD']),
                        data=json.dumps({'message': 'post to ' + url,
                                         'content': c}))
