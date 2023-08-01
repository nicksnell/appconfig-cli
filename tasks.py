from invoke import task


@task
def lint(c):
    c.run("black appconf tests")
    c.run("ruff appconf tests")


@task
def test(c):
    c.run("pytest")
