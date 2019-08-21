from invoke import task


@task
def run(c):
    c.run('python -m main')


@task
def test(c):
    c.run('nosetests')


@task
def build(c):
    c.run('docker image build -t micropub:0.1 .')
