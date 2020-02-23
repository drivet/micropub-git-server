import json
import datetime
import copy
import os

from jsonschema import validate
from flask import Response, Blueprint
from flask import current_app as app
from flask import request
from flask_indieauth import requires_indieauth
from micropub.mf2schema import mf2schema
from micropub.utils import disable_if_testing
from indieweb_utils.notedown import extract_links
from indieweb_utils.unfurl import PreviewGenerator
from indieweb_utils.commit import commit


FULL_CONFIG_TEMPLATE = '''{{
    "syndicate-to": {syndicate_to},
    "media-endpoint": "{media_endpoint}"
}}
'''


SYNDICATE_CONFIG_TEMPLATE = '''{{
    "syndicate-to": {syndicate_to}
}}
'''


MEDIA_CONFIG_TEMPLATE = '''{{
    "media-endpoint": "{media_endpoint}"
}}
'''


micropub_bp = Blueprint('micropub_bp', __name__)

preview_generator = None


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
    media_endpoint = os.environ.get('MICROPUB_MEDIA_ENDPOINT', None)
    syndicate_to = os.environ.get('MICROPUB_SYNDICATE_TO', None)
    if q == 'config':
        if not media_endpoint and not syndicate_to:
            return "{}"
        elif media_endpoint and not syndicate_to:
            return MEDIA_CONFIG_TEMPLATE.format(media_endpoint=media_endpoint)
        elif not media_endpoint and syndicate_to:
            return SYNDICATE_CONFIG_TEMPLATE.format(syndicate_to=syndicate_to)
        else:
            return FULL_CONFIG_TEMPLATE.format(media_endpoint=media_endpoint,
                                               syndicate_to=syndicate_to)
    elif q == 'syndicate-to':
        if not syndicate_to:
            return "[]"
        else:
            return SYNDICATE_CONFIG_TEMPLATE.format(syndicate_to=syndicate_to)
    else:
        app.logger.error(f'Unsupported q value: {q}')
        return Response(status=400)


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
    permalink = os.path.join(app.config['ME'], make_permalink(request_data))

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
    app.logger.info('saving post...')
    props = request_data['properties']
    published_date = get_published_date(props)
    slug = get_slug(props)
    repo_path = get_repo_path_format().format(published=published_date,
                                              slug=slug)
    files = {repo_path: json.dumps(request_data)}

    if is_preview_enabled():
        app.logger.info('previewing is enabled...')
        preview = unfurl_post(request_data)
        if preview:
            app.logger.info('generated preview')
            path_format = get_preview_path_format()
            preview_path = path_format.format(published=published_date,
                                              slug=slug)
            app.logger.info(f'saving preview at {preview_path}')
            files[preview_path] = json.dumps(preview)
    else:
        app.logger.info('previewing is disabled, not generating preview...')

    auth = (os.environ['GITHUB_USERNAME'], os.environ['GITHUB_PASSWORD'])
    commit(os.environ['GITHUB_REPO'], auth, files, 'new post')


def unfurl_post(request_data):
    preview_url = get_preview_url(request_data)
    if not preview_url:
        app.logger.info('did not find preview URL')
        return None
    app.logger.info(f'found preview URL {preview_url}')
    return generate_preview(preview_url)


def generate_preview(url):
    global preview_generator
    if not preview_generator:
        preview_generator = PreviewGenerator()
        preview_generator.initialize()
    return preview_generator.preview(url)


def get_preview_url(post):
    props = post['properties']
    if 'like-of' in props:
        return props['like-of'][0]

    if 'in-reply-to' in props:
        return props['in-reply-to'][0]

    if 'repost-of' in props:
        return props['repost-of'][0]

    if 'bookmark-of' in props:
        return props['bookmark-of'][0]

    if 'content' in props:
        links = extract_links(props['content'][0])
        if links:
            return links[0]

    return None


def is_preview_enabled():
    return os.environ.get('MICROPUB_PREVIEW_ENABLED', '')


def get_preview_path_format():
    default = '/previews/{published:%Y}/{published:%m}/{published:%d}/{slug}'
    return os.environ.get('MICROPUB_PREVIEW_PATH_FORMAT', default)


def get_repo_path_format():
    default = '/content/micropub/' + \
              '{published:%Y}/{published:%m}/{published:%d}/' + \
              '{published:%H}{published:%M}{published:%S}.mp'
    return os.environ.get('MICROPUB_REPO_PATH_FORMAT', default)


def make_permalink(request_data):
    props = request_data['properties']
    published_date = get_published_date(props)
    slug = get_slug(props)
    return get_permalink_format().format(published=published_date, slug=slug)


def get_permalink_format():
    default = '{published:%Y}/{published:%m}/{published:%d}/{slug}'
    return os.environ.get('MICROPUB_PERMALINK_FORMAT', default)


def get_slug(props):
    return props.get('mp-slug', [get_default_slug(props)])[0]


def get_default_slug(props):
    date = get_published_date(props)
    return '{published:%H}{published:%M}{published:%S}'.format(published=date)


def get_published_date(props):
    datestr = props['published'][0]
    try:
        return datetime.datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        return datetime.datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S-%f')
