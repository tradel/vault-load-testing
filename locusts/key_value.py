import json
import sys

import os
import random

from locust import HttpLocust, task

sys.path.append(os.getcwd())
import common
from locusts import VaultLoadTaskSet


class KeyValueTasks(VaultLoadTaskSet):

    @task
    def get_kv_secret(self):
        path = '/v1/secret/%s' % random.choice(self.testdata['keys'])
        self.client.get(path,
                        name='/v1/secret/[key1]/[key2]')

    @task
    def put_kv_secret(self):
        path = '/v1/secret/%s' % random.choice(self.testdata['keys'])
        self.client.put(path,
                        json={'value': common.random_data(self.testdata['secret_size'])},
                        name='/v1/secret/[key1]/[key2]')

    @task
    def list_l1_secrets(self):
        self.client.request('LIST', '/v1/secret',
                            name='/v1/secret')

    @task
    def list_l2_secrets(self):
        self.client.request('LIST', '/v1/secret/%s' % common.key_path_1(),
                            name='/v1/secret/[key1]')


class KeyValueLocust(HttpLocust):
    task_set = KeyValueTasks
    weight = 3
    min_wait = 5000
    max_wait = 10000
