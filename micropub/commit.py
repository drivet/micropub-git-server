import requests

GITHUB_API_ROOT = 'https://api.github.com'


def commit(repo, auth, files, message, branch="master"):
    """
    repo is the repository to commit the files to
    files is a dictionary of relative file paths and contents,
    either new or updated.  Everything committed in one shot.
    """
    old_commit = get_latest_commit(repo, auth, branch)
    old_tree = get_tree(repo, auth, old_commit)
    blobs = {}
    for path in files.keys():
        contents = files[path]
        blobs[path] = create_blob(repo, auth, contents)
    new_tree = create_tree(repo, auth, old_tree, blobs)
    new_commit = create_commit(repo, auth, old_commit, new_tree, message)
    update_branch(repo, auth, new_commit, branch)


def get_latest_commit(repo, auth, branch):
    body = get(f'{GITHUB_API_ROOT}/repos/{repo}/git/ref/heads/{branch}', auth)
    sha = body['object']['sha']
    return get_commit(repo, auth, sha)


def get_commit(repo, auth, sha):
    return get(f'{GITHUB_API_ROOT}/repos/{repo}/git/commits/{sha}', auth)


def get_tree(repo, auth, commit):
    tree_sha = commit['tree']['sha']
    return get(f'{GITHUB_API_ROOT}/repos/{repo}/git/trees/{tree_sha}', auth)


def create_blob(repo, auth, content):
    post_data = {'content': content, 'encoding': 'utf-8'}
    return post(f'{GITHUB_API_ROOT}/repos/{repo}/git/blobs', auth, post_data)


def create_tree(repo, auth, old_tree, blobs):
    post_data = {
        'base_tree': old_tree['sha'],
        'tree': []
    }
    for path in blobs.keys():
        tree = {}
        tree['path'] = path
        tree['type'] = 'blob'
        tree['mode'] = '100644'
        tree['sha'] = blobs[path]['sha']
        post_data['tree'].append(tree)

    return post(f'{GITHUB_API_ROOT}/repos/{repo}/git/trees', auth, post_data)


def create_commit(repo, auth, old_commit, new_tree, message):
    post_data = {
        'message': message,
        'tree': new_tree['sha'],
        'parents': [old_commit['sha']]
    }
    return post(f'{GITHUB_API_ROOT}/repos/{repo}/git/commits', auth, post_data)


def update_branch(repo, auth, new_commit, branch):
    branch_ref = f'refs/heads/{branch}'
    patch_data = {
        'sha': new_commit['sha']
    }
    return patch(f'{GITHUB_API_ROOT}/repos/{repo}/git/{branch_ref}',
                 auth, patch_data)


def get(url, auth):
    r = requests.get(url, auth=auth)
    if r.status_code != 200:
        raise Exception(f'GET {url} failed with {r.status_code}, {r.json()}')
    else:
        return r.json()


def post(url, auth, data):
    r = requests.post(url, auth=auth, json=data)
    if r.status_code != 201:
        raise Exception(f'POST {url} failed with {r.status_code}, {r.json()}')
    else:
        return r.json()


def patch(url, auth, data):
    r = requests.patch(url, auth=auth, json=data)
    if r.status_code != 200:
        raise Exception(f'PATCH {url} failed with {r.status_code}, {r.json()}')
    else:
        return r.json()