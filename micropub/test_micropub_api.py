import json
from micropub import app

ctx = None
client = None


def setup_module():
    global ctx
    ctx = app.app_context()
    global client
    client = app.test_client()
    app.config['TESTING'] = True
    app.config['PERMALINK_FORMAT'] = '{published:%Y}/{published:%m}/{published:%d}/{slug}'


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


def test_returns_success():
    rv = client.post('/', data={
        'content': 'hello',
        'mp_slug': 'blub'
    })
    assert rv.status_code == 202


def teardown_module():
    pass
