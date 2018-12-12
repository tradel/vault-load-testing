#!/usr/bin/env python3

import common
import requests
import click
import json
from typing import List
from common import get_kv_version


def populate(host: str, count: int, size: int, token: str) -> List[str]:

    click.echo('\nChecking Vault KV version...')
    kv_version = get_kv_version(host=host, token=token)
    click.echo(click.style(f'Using Vault KV version {kv_version}\n', bold=True, fg='white'))

    s = requests.Session()
    s.headers = {'X-Vault-Token': token}
    paths = []
    with click.progressbar(range(count), label='Creating test keys in Vault') as bar:
        for _ in bar:
            path = common.key_path()
            if kv_version == 1:
                r = s.post(f'{host}/v1/secret/test/{path}', json={'value': common.random_data(size)})
            else:
                r = s.post(f'{host}/v1/secret/data/test/{path}', json={'data': {'value': common.random_data(size)}})

            if r.status_code >= 400:
                try:
                    for msg in r.json()['warnings']:
                        click.echo(click.style(f'Error returned by Vault: {msg}', bold=True, fg='yellow'), err=True)
                except KeyError:
                    pass
                r.raise_for_status()
            else:
                paths.append(path)

    return paths


@click.command()
@click.option('--secrets', default=1000,
              help='Number of test secrets to create')
@click.option('--secret-size', default=1024,
              help='Size of each secret, in bytes')
@click.option('--transit-size', default=1048576,
              help='Size of data blocks to encrypt for Transit tests, in bytes')
@click.option('--host', '-H', default='http://localhost:8200',
              help='URL of the Vault server to test')
@click.argument('token', envvar='VAULT_TOKEN')
def main(host, secrets, secret_size, transit_size, token):
    paths = populate(host, secrets, secret_size, token)
    with open('testdata.json', 'w') as f:
        json.dump({
            'token': token,
            'num_secrets': secrets,
            'secret_size': secret_size,
            'transit_size': transit_size,
            'keys': paths,
        }, f)


if __name__ == '__main__':
    main()
