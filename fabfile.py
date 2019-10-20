import os
from fabric import task

branch = os.environ['CIRCLE_BRANCH']

if branch == 'master':
    port = 3132
else:
    port = 3131

os.environ['PORT'] = f'{port}'

if branch == 'master':
    volume = 'mp-root'
else:
    volume = 'mp-root-test'


image = f'desmondrivet/micropub-git-server:{branch}'
name = 'micropub-git-server'


env = ['ME', 'TOKEN_ENDPOINT', 'GITHUB_REPO',
       'GITHUB_USERNAME', 'GITHUB_PASSWORD', 'HOST']


def all_env_cmd():
    return ' && '.join([env_cmd(e) for e in env])


def env_cmd(e):
    return 'export ' + e + '="' + os.environ[e] + '"'


def docker_env_params():
    return ' '.join([f'-e {e}' for e in env])


@task(hosts=["dcr@micropub.desmondrivet.com"])
def deploy(c):
    c.run(f'docker pull {image}')
    c.run(f'docker stop {name}', warn=True)
    c.run(f'{all_env_cmd()} && docker run --name {name} ' +
          f'{docker_env_params()} ' +
          f'-p {port}:3031 ' +
          f'-v {volume}:/data --rm -d {image}')
