import sys
import os
import random

from locust import task

sys.path.append(os.getcwd())
from locusts import VaultTaskSet, VaultLocust


class AppRoleTaskSet(VaultTaskSet):
    ROLE_NAME = 'test-approle'
    SECRET_NAME = 'test-secret'
    role_id = None
    secrets = []

    def setup(self):
        self.enable_auth('approle')
        self.create_approle()

    def teardown(self):
        self.client.delete(f'/v1/auth/approle/role/{self.ROLE_NAME}')

    def create_approle(self):
        self.client.post(f'/v1/auth/approle/role/{self.ROLE_NAME}')
        r = self.client.get(f'/v1/auth/approle/role/{self.ROLE_NAME}/role-id')
        self._set_roleid(r.json()['data']['role_id'])

    @classmethod
    def _set_roleid(cls, role_id):
        cls.role_id = role_id

    @classmethod
    def _append_secret(cls, secret_id, accessor):
        cls.secrets.append((secret_id, accessor))

    @task
    def create_secret(self):
        r = self.client.post(f'/v1/auth/approle/role/{self.ROLE_NAME}/secret-id')
        secret_id = r.json()['data']['secret_id']
        accessor = r.json()['data']['secret_id_accessor']
        self._append_secret(secret_id, accessor)

    @task
    def auth_success(self):
        try:
            secret = random.choice(self.secrets)
            self.client.post('/v1/auth/approle/login',
                             json={'role_id': self.role_id,
                                   'secret_id': secret[0]})
        except IndexError:
            pass

    @task
    def auth_failure(self):
        try:
            secret = random.choice(self.secrets)
            with self.client.post('/v1/auth/approle/login',
                                  json={'role_id': self.role_id,
                                        'secret_id': secret[0] + 'XXX'},
                                  catch_response=True) as r:
                if r.status_code == 400 and ('failed to validate credentials' in r.json()['errors'][0]
                                             or 'invalid secret id' in r.json()['errors'][0]):
                    r.success()
                else:
                    r.failure('unexpected response to bad auth token: ' + r.content.decode('utf-8'))
        except IndexError:
            pass


class AppRoleLocust(VaultLocust):
    task_set = AppRoleTaskSet
    weight = 1
    min_wait = 5000
    max_wait = 10000
