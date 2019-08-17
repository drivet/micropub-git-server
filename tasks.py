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


@task
def buildnginx(c):
    c.run('docker image build -t nginx-micropub:0.1 nginx/')


@task
def runnginx(c):
    c.run('docker run --name nginx-micropub -p 80:80 --rm -d ' +
          'nginx-micropub:0.1')
