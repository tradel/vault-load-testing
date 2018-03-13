#!/usr/bin/env python3

import common
import requests
import click
import json


def populate(host, count, size, token):
    s = requests.Session()
    s.headers = {'X-Vault-Token': token}
    paths = []
    with click.progressbar(range(count), label='Creating test keys in Vault') as bar:
        for _ in bar:
            path = common.key_path()
            r = s.post(f'{host}/v1/secret/{path}', json={'value': common.random_data(size)})
            r.raise_for_status()
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
@click.argument('token', envvar='TOKEN')
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
