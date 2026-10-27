"""Version B of a synthetic integer-ceiling test. Separate source revision."""

def check(value, ceiling):
    if type(ceiling) is not int or type(value) is not int:
        raise TypeError('integer operands required')
    return 'pass' if value <= ceiling else 'fail'
