from fabric import task

image = 'desmondrivet/micropub-git-server:master'
testvolume = '/var/local/micropub-test'
volume = '/var/local/micropub'
name = 'micropub-git-server'
testport = 3031
port = 3032


@task
def deploytest(c):
    c.run(f'docker pull {image}')
    c.run(f'docker stop {name}', warn=True)
    c.run(f'docker run --name {name} -p {testport}:3031 ' +
          f'-v {testvolume}:/var/local/micropub --rm -d {image}')


@task
def deploy(c):
    c.run(f'docker pull {image}')
    c.run(f'docker stop {name}', warn=True)
    c.run(f'docker run --name {name} -p {port}:3031 ' +
          f'-v {volume}:/var/local/micropub --rm -d {image}')
