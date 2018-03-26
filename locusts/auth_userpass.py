import sys
import os

from locust import task

sys.path.append(os.getcwd())
from common import random_data
from locusts import VaultTaskSet, VaultLocust


class UserPassAuthTasks(VaultTaskSet):
    USER_NAME = 'test-user'
    password = None

    def setup(self):
        self.enable_auth('userpass')
        self.reset_password()

    def teardown(self):
        self.client.delete(f'/v1/auth/userpass/users/{self.USER_NAME}')

    @classmethod
    def _set_password(cls):
        cls.password = random_data(16)
        return cls.password

    @task
    def auth_success(self):
        self.client.post(f'/v1/auth/userpass/login/{self.USER_NAME}',
                         json={'password': UserPassAuthTasks.password})

    @task
    def auth_failure(self):
        with self.client.post(f'/v1/auth/userpass/login/{self.USER_NAME}',
                              json={'password': random_data(16)},
                              catch_response=True) as r:
            if r.status_code == 400 and 'invalid username or password' in r.json()['errors']:
                r.success()
            else:
                r.failure('unexpected response to invalid login')

    @task
    def reset_password(self):
        self.client.post(f'/v1/auth/userpass/users/{self.USER_NAME}',
                         json={'password': UserPassAuthTasks._set_password()})


class UserPassAuthLocust(VaultLocust):
    task_set = UserPassAuthTasks
    weight = 1
    min_wait = 5000
    max_wait = 10000
