
from micropub.format import make_post

def assertPost(result, type, fm, content):
    assert result[1] == type
    #print(result[0])
    #print(f"---\n{fm}\n---\n\n{content}")
    assert result[0] == f"---\n{fm}\n---\n\n{content}"

def test_published_date():
    reqdata = {
        'type': ['h-entry'],
        'properties': {
            'content': ['hello'],
            'published': ['2019-08-15T14:35:45+00:00']
        }
    }
    result = make_post(reqdata)
    assertPost(result, 'md', "date: '2019-08-15T14:35:45+00:00'", 'hello')
    

def test_name_title():
    reqdata = {
        'type': ['h-entry'],
        'properties': {
            'content': ['hello'],
            'name': ['this is a title']
        }
    }
    result = make_post(reqdata)
    assertPost(result, 'md', "title: this is a title", 'hello')
    
def test_reply_to():
    reqdata = {
        'type': ['h-entry'],
        'properties': {
            'content': ['hello'],
            'name': ['this is a title'],
            'in-reply-to': ['http://example.com/bad-take']
        }
    }
    result = make_post(reqdata)
    assertPost(result, 'md', 
                "in-reply-to: http://example.com/bad-take\ntitle: this is a title",
                'hello')

def test_category():
    reqdata = {
        'type': ['h-entry'],
        'properties': {
            'content': ['hello'],
            'category': ['tag1', 'tag2']
        }
    }
    result = make_post(reqdata)
    assertPost(result, 'md', "tags:\n- tag1\n- tag2", 'hello')
 