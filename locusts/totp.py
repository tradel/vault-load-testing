import sys
import os
import common

from locust import task
from locusts import VaultTaskSet, VaultLocust


class TotpTasks(VaultTaskSet):
    KEY_NAME = 'test-totp-key'
    ISSUER = 'Vault'
    ACCOUNT_NAME = 'test@test.com'

    def setup(self):
        self.mount('totp')
        if not self.is_in_list(self.KEY_NAME, '/v1/totp/keys'):
            self.client.post(f'/v1/totp/keys/{self.KEY_NAME}',
                             json={'generate': True,
                                   'issuer': self.ISSUER,
                                   'account_name': self.ACCOUNT_NAME})

    @task
    def generate(self):
        r = self.client.get(f'/v1/totp/code/{self.KEY_NAME}')


class TotpLocust(VaultLocust):
    task_set = TotpTasks
    weight = 1
    min_wait = 5000
    max_wait = 60000
