from invoke import task


@task
def run(c):
    c.run('python -m main')


@task
def test(c):
    c.run('nosetests')


@task
def dbuild(c):
    c.run('docker image build -t ' +
          'desmondrivet/micropub-git-server:$CIRCLE_BRANCH .')


@task
def dlogin(c):
    c.run('echo "$DOCKER_PASS" | ' +
          'docker login --username $DOCKER_USER --password-stdin')


@task
def dpush(c):
    c.run('docker push desmondrivet/micropub-git-server:$CIRCLE_BRANCH')
