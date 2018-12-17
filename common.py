import random
import string
from locust.clients import HttpSession
import requests


def random_hex(size) -> str:
    return ''.join([random.choice(string.hexdigits) for _ in range(size)]).lower()


def key_path_1() -> str:
    return random_hex(2)


def key_path_2() -> str:
    return random_hex(32)


def key_path() -> str:
    return '%s/%s' % (key_path_1(), key_path_2())


def random_data(size) -> str:
    return ''.join([random.choice(string.ascii_letters) for _ in range(size)])


def get_kv_version(client: requests.Session=None, host: str=None, token: str=None) -> int:
    if isinstance(client, HttpSession):
        s = client
        r = s.get('/v1/sys/mounts')
    elif isinstance(client, requests.Session):
        s = client
        r = s.get(f'{host}/v1/sys/mounts')
    else:
        s = requests.Session()
        s.headers = {'X-Vault-Token': token}
        r = s.get(f'{host}/v1/sys/mounts')

    r.raise_for_status()

    version = 1
    for key, val in r.json().items():
        if key == 'secret/':
            if 'options' in val:
                version = int(val['options'].get('version', 1))
            break

    return version
