import yaml
from dateutil.parser import parse

# default behaviour is to copy the properties as is to the front matter.
# this will change that behaviour for certain fields
prop_transform = {
    'name': {
        'prop': 'title',
        'policy': 'first'
    },
    'in-reply-to': {
        'policy': 'first'
    },
    'like-of': {
        'policy': 'first'
    },
    'repost-of': {
        'policy': 'first'
    },
    'bookmark-of': {
        'policy': 'first'
    },
    'published': {
        'prop': 'date',
        'policy': 'first'
    },
    'updated': {
        'prop': 'modified',
        'policy': 'first'
    },
    'category': {
        'prop': 'tags',
    },
    'summary': {
        'policy': 'first'
    },
    'location': {
        'policy': 'first'
    },
    'content': {
        'policy': 'skip'
    }
}

def tziso(notz):
    d = parse(notz)
    return d.astimezone().replace(microsecond=0).isoformat()

# returns two element array
# - the post as a string
# - the file extension (md or html)
def make_post(data):
    assert len(data['type']) == 1
    assert data['type'][0] == 'h-entry'
    
    frontmatter = {}
    properties = data['properties']
    for key in properties.keys():
        if key in prop_transform:
            transform = prop_transform[key]
            dest_prop = transform.get('prop', key)
            policy = transform.get('policy', 'copy')
            if policy == 'skip':
                continue
            if policy == 'first':
                frontmatter[dest_prop] = properties[key][0]
            elif policy == 'copy':
                frontmatter[dest_prop] = properties[key]
        else:
            frontmatter[key] = properties[key]
    
    if not frontmatter:
        raise 'at least one data property needed in a post'
    
    if 'date' in frontmatter:
        frontmatter['date'] = tziso(frontmatter['date'])

    if 'modified' in frontmatter:
        frontmatter['modified'] = tziso(frontmatter['modified'])

    post_content = None
    post_type = 'md'
    if 'content' in properties and \
            properties['content'] and \
            isinstance(properties['content'], list):
        content = properties['content'][0]
        if type(content) is dict and 'html' in content:
            post_content = content['html']
            post_type = 'html'
        elif type(content) is str:
            post_content = content
    
    frontmatter_str = yaml.safe_dump(frontmatter)
    
    post = f'---\n{frontmatter_str}---\n'
    if post_content:
        post = f'{post}\n{post_content}'
   
    return [post, post_type]
