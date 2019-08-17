from micropub import app
from micropub.micropub_json import form2json, extract_create_request
from werkzeug.datastructures import MultiDict


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
            'content': ['hello']
        }
    }
    assert extract_create_request(json, None) == json


def test_json_overrides_form_data():
    json = {
        'type': ['h-entry'],
        'properties': {
            'content': ['good-bye']
        }
    }
    form = {
        'h': 'entry',
        'content': 'hello'
    }
    assert extract_create_request(json, form) == json


def test_form_used_if_no_json():
    json = {
        'type': ['h-entry'],
        'properties': {
            'content': ['hello']
        }
    }
    form = {
        'h': 'entry',
        'content': 'hello'
    }
    assert extract_create_request(None, form) == json


def test_should_make_permalink():
    app.config['PERMALINK_FORMAT'] = 'hello'


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
