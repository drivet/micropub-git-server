import os
import json
from unittest.mock import patch
from micropub import app
from micropub.micropub import form2json, extract_create_request, \
    make_permalink
from werkzeug.datastructures import MultiDict

ctx = None
client = None


def setup_module():
    global ctx
    ctx = app.app_context()
    global client
    client = app.test_client()
    app.config['TESTING'] = True
    datef = '{published:%Y}/{published:%m}/{published:%d}'
    timef = '{published:%H}{published:%M}{published:%S}'
    os.environ['MICROPUB_PERMALINK_FORMAT'] = datef + '/{slug}'
    os.environ['GITHUB_REPO'] = 'drivet/pelican-test-blog'
    os.environ['MICROPUB_REPO_PATH_FORMAT'] = '/' + datef + '/' + timef + '.mpj'


def test_get_fails_with_no_query():
    rv = client.get('/')
    assert rv.status_code != 200


def test_post_fails_with_action():
    rv = client.post('/', data={'action': 'delete'})
    assert rv.status != 200


def test_only_get_and_post_supported():
    rv = client.delete('/')
    assert rv.status_code == 405

    rv = client.put('/')
    assert rv.status_code == 405


def xtest_returns_empty_config():
    rv = client.get('/?q=config')
    assert rv.status_code == 200
    assert len(rv.data) > 0
    print(rv.data)
    assert rv.data == b"{}"


def xtest_returns_empty_syndicate_targets():
    rv = client.get('/?q=syndicate-to')
    assert rv.status_code == 200
    assert len(rv.data) > 0
    assert rv.data == b"[]"


def xtest_returns_media_endpoint():
    os.environ['MICROPUB_MEDIA_ENDPOINT'] = 'https://media.example.com'
    rv = client.get('/?q=config')
    assert rv.status_code == 200
    assert len(rv.data) > 0
    jdict = json.loads(rv.data)
    assert len(jdict) == 1
    assert jdict['media-endpoint'] == 'https://media.example.com'


def xtest_returns_syndicate_targets():
    os.environ['MICROPUB_SYNDICATE_TO'] = \
        '[{"uid": "twitter", "name": "Twitter"}]'
    rv = client.get('/?q=syndicate-to')
    assert rv.status_code == 200
    assert len(rv.data) > 0
    jdict = json.loads(rv.data)
    assert len(jdict) == 1
    targets = jdict['syndicate-to']
    assert len(targets) == 1
    assert targets[0]['uid'] == 'twitter'
    assert targets[0]['name'] == 'Twitter'


def test_returns_all_config():
    os.environ['MICROPUB_SYNDICATE_TO'] = \
        '[{"uid": "twitter", "name": "Twitter"}]'
    os.environ['MICROPUB_MEDIA_ENDPOINT'] = 'https://media.example.com'
    rv = client.get('/?q=config')
    assert rv.status_code == 200
    assert len(rv.data) > 0
    jdict = json.loads(rv.data)
    assert len(jdict) == 2
    assert jdict['media-endpoint'] == 'https://media.example.com'
    targets = jdict['syndicate-to']
    assert len(targets) == 1
    assert targets[0]['uid'] == 'twitter'
    assert targets[0]['name'] == 'Twitter'


@patch('micropub.micropub.commit_file')
def test_returns_success(commit_mock):
    class Response:
        pass
    r = Response()
    r.status_code = 201
    commit_mock.return_value = r

    rv = client.post('/', data={
        'content': 'hello',
        'mp-slug': 'blub',
        'published': '2019-07-16T13:45:23.5'
    })
    assert rv.status_code == 202
    url = 'https://api.github.com/repos/drivet/pelican-test-blog/contents/2019/07/16/134523.mpj'
    contents = '{"type": ["h-entry"], "properties": {"content": ["hello"], "mp-slug": ["blub"], "published": ["2019-07-16T13:45:23.5"]}}'
    commit_mock.assert_called_with(url, contents)
    assert rv.headers['Location'] == 'http://localhost/2019/07/16/blub'


@patch('micropub.micropub.commit_file')
def test_should_delete_access_token(commit_mock):
    class Response:
        pass
    r = Response()
    r.status_code = 201
    commit_mock.return_value = r
    
    rv = client.post('/', data={
        'content': 'hello',
        'mp-slug': 'blub',
        'published': '2019-07-16T13:45:23.5',
        'access_token': 'ZZZZSSSS'
    })
    assert rv.status_code == 202
    url = 'https://api.github.com/repos/drivet/pelican-test-blog/contents/2019/07/16/134523.mpj'
    contents = '{"type": ["h-entry"], "properties": {"content": ["hello"], "mp-slug": ["blub"], "published": ["2019-07-16T13:45:23.5"]}}'
    commit_mock.assert_called_with(url, contents)
    assert rv.headers['Location'] == 'http://localhost/2019/07/16/blub'


def test_badly_formatted_json_throws():
    try:
        extract_create_request('this is not good json', None)
    except Exception:
        pass
    else:
        assert False


def test_bad_micropub_json_throws():
    try:
        extract_create_request({"stuff": "blah"}, None)
    except Exception:
        pass
    else:
        assert False


def test_good_micropub_json_is_validated():
    json = {
        'type': ['h-entry'],
        'properties': {
            'content': ['hello'],
            'published': ['2019-08-15T14:35:45.5']
        }
    }
    assert extract_create_request(json, None) == json


def test_json_overrides_form_data():
    json = {
        'type': ['h-entry'],
        'properties': {
            'content': ['good-bye'],
            'published': ['2019-08-15T14:35:45.5']
        }
    }
    form = {
        'h': 'entry',
        'content': 'hello',
        'published': '2019-08-15T14:35:45.5'
    }
    assert extract_create_request(json, form) == json


def test_form_used_if_no_json():
    json = {
        'type': ['h-entry'],
        'properties': {
            'content': ['hello'],
            'published': ['2019-08-15T14:35:45.5']
        }
    }
    form = {
        'h': 'entry',
        'content': 'hello',
        'published': '2019-08-15T14:35:45.5'
    }
    assert extract_create_request(None, form) == json


def test_default_published_data_is_filled_in():
    form = {
        'content': 'hello'
    }

    result = extract_create_request(None, form)
    assert result['type'] == ['h-entry']
    assert len(result['properties']['published']) == 1
    assert len(result['properties']['published'][0]) > 0


def test_should_make_permalink():
    with app.app_context():
        app.config['PERMALINK_FORMAT'] = \
              '{published:%Y}/{published:%m}/{published:%d}/{slug}'
        request_data = {
            'type': 'h-entry',
            'properties': {
                'mp-slug': ['blub'],
                'published': ['2019-08-15T14:16:34.6']
            }
        }
        permalink = make_permalink(request_data)
        print(permalink)
        assert permalink == '2019/08/15/blub'


def test_should_handle_missing_slug_in_permalink():
    with app.app_context():
        app.config['PERMALINK_FORMAT'] = \
              '{published:%Y}/{published:%m}/{published:%d}/{slug}'
        request_data = {
            'type': 'h-entry',
            'properties': {
                'published': ['2019-08-15T14:16:34.6']
            }
        }
        permalink = make_permalink(request_data)
        assert permalink == '2019/08/15/141634'


def test_form_converted_to_json():
    form = MultiDict()
    form.setlist('h[]', ['entry', 'review'])
    form['in-reply-to'] = 'some-post'
    form.setlist('syndicate[]', ['twitter', 'facebook'])

    result = form2json(form)
    assert result['type'] == ['h-entry', 'h-review']
    assert result['properties']['in-reply-to'] == ['some-post']
    assert result['properties']['syndicate'] == ['twitter', 'facebook']


def test_h_entry_is_default_in_forms():
    form = MultiDict()
    form['in-reply-to'] = 'some-post'

    result = form2json(form)
    assert result['type'] == ['h-entry']
    assert result['properties']['in-reply-to'] == ['some-post']
