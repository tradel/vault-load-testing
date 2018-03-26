import sys
import os

from locust import HttpLocust, task

sys.path.append(os.getcwd())
from locusts import VaultTaskSet, VaultLocust


class PkiTasks(VaultTaskSet):
    DOMAIN_NAME = 'example.com'
    ROLE_NAME = 'test-pki-role'

    def setup(self):
        self.mount('pki')
        self.client.post('/v1/pki/root/generate/internal',
                         json={'common_name': self.DOMAIN_NAME, 'ttl': '8760h'})
        self.create_role()

    def teardown(self):
        self.delete_role()

    def create_role(self):
        if self.is_in_list(self.ROLE_NAME, '/v1/pki/roles'):
            self.delete_role()
        self.client.post(f'/v1/pki/roles/{self.ROLE_NAME}',
                         json={'allowed_domains': self.DOMAIN_NAME,
                               'max_ttl': '72h',
                               'allow_subdomains': True})

    def delete_role(self):
        self.client.delete(f'/v1/pki/roles/{self.ROLE_NAME}')

    @task
    def generate_cert(self):
        self.client.post('/v1/pki/issue/test-pki-role',
                         json={'common_name': f'foo.{self.DOMAIN_NAME}'})


class PkiLocust(VaultLocust):
    task_set = PkiTasks
    weight = 1
    min_wait = 5000
    max_wait = 10000
