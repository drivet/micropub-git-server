from invoke import task


@task
def run(c):
    print("Hello!")


@task
def build(c):
    c.run('docker image build -t micropub:0.1 .')


@task
def composeup(c):
    pass
