import json
import sys

import os
import random

from locust import HttpLocust, task

sys.path.append(os.getcwd())
import common

from locusts import VaultTaskSet, VaultLocust


class KeyValueTasks(VaultTaskSet):

    def __init__(self, parent):
        super().__init__(parent)
        self.kv_version = 1

    def on_start(self):
        self.kv_version = common.get_kv_version(client=self.client)

    @task
    def get_kv_secret(self):
        key = random.choice(self.locust.testdata['keys'])
        if self.kv_version == 1:
            self.client.get(f'/v1/secret/test/{key}', name='/v1/secret/[key1]/[key2]')
        else:
            self.client.get(f'/v1/secret/data/test/{key}', name='/v1/secret/[key1]/[key2]')

    @task
    def put_kv_secret(self):
        key = random.choice(self.locust.testdata['keys'])
        payload = common.random_data(self.locust.testdata['secret_size'])
        if self.kv_version == 1:
            self.client.put(f'/v1/secret/test/{key}',
                            json={'value': payload},
                            name='/v1/secret/test/[key1]/[key2]')
        else:
            self.client.put(f'/v1/secret/data/test/{key}',
                            json={'data': {'value': payload}},
                            name='/v1/secret/test/[key1]/[key2]')

    @task
    def list_l1_secrets(self):
        if self.kv_version == 1:
            self.client.request('LIST', '/v1/secret/test', name='/v1/secret/test')
        else:
            self.client.request('LIST', '/v1/secret/metadata/test', name='/v1/secret/test')

    @task
    def list_l2_secrets(self):
        key_path = common.key_path_1()
        if self.kv_version == 1:
            self.client.request('LIST', f'/v1/secret/test/{key_path}', name='/v1/secret/test/[key1]')
        else:
            self.client.request('LIST', f'/v1/secret/metadata/test/{key_path}', name='/v1/secret/test/[key1]')


class KeyValueLocust(VaultLocust):
    task_set = KeyValueTasks
    weight = 3
    min_wait = 5000
    max_wait = 10000
