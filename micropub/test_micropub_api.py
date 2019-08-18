import json
from unittest.mock import patch
from micropub import app

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
    app.config['PERMALINK_FORMAT'] = datef + '/{slug}'
    app.config['REPO_URL_ROOT'] = 'https://api.guthub.com/drivet/pelican-test-blog'
    app.config['REPO_PATH_FORMAT'] = '/' + datef + '/' + timef + '.mpj'


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


def test_returns_config():
    rv = client.get('/?q=config')
    assert rv.status_code == 200
    assert len(rv.data) > 0
    assert len(json.loads(rv.data).keys()) > 0


@patch('micropub.micropub.commit_file')
def test_returns_success(commit_mock):
    rv = client.post('/', data={
        'content': 'hello',
        'mp_slug': 'blub',
        'published': '2019-07-16T13:45:23.5'
    })
    assert rv.status_code == 202
    url = app.config['REPO_URL_ROOT'] + '/2019/07/16/134523.mpj'
    contents = '{"type": ["h-entry"], "properties": {"content": ["hello"], "mp_slug": ["blub"], "published": ["2019-07-16T13:45:23.5"]}}'
    commit_mock.assert_called_with(url, contents)
    print(rv.headers['Location'])
    assert rv.headers['Location'] == 'http://localhost/2019/07/16/blub'


def teardown_module():
    pass
