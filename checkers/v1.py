"""Version A of a synthetic integer-ceiling test. No external inputs."""

def check(value, ceiling):
    if type(value) is not int or type(ceiling) is not int:
        raise TypeError('integer operands required')
    return 'fail' if value > ceiling else 'pass'
