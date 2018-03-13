import random
import string


def random_hex(size):
    return ''.join([random.choice(string.hexdigits) for _ in range(size)]).lower()


def key_path_1():
    return random_hex(2)


def key_path_2():
    return random_hex(32)


def key_path():
    return '%s/%s' % (key_path_1(), key_path_2())


def secret_path():
    return '/v1/secret/%s' % key_path()


def random_data(size):
    return ''.join([random.choice(string.ascii_letters) for _ in range(size)])
