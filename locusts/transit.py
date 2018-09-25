import json
import sys

import base64
import os

from locust import HttpLocust, task
from locust.clients import HttpSession

sys.path.append(os.getcwd())
import common

from locusts import VaultTaskSet, VaultLocust


class TransitTasks(VaultTaskSet):

    def on_start(self):
        self.mount('transit')

    @task
    def encrypt_block(self):
        data = common.random_data(self.locust.testdata['transit_size'])
        data = base64.b64encode(data.encode()).decode()
        self.client.headers['Content-Type'] = "application/json"
        response = self.client.post('/v1/transit/encrypt/test',
                                    json={'plaintext': data})
        json_response_dict = response.json()
        self.locust.testdata['encrypted_data'] = json_response_dict['data']['ciphertext']
        self.decrypt_block()

    def decrypt_block(self):
        data = self.locust.testdata['encrypted_data']
        self.client.headers['Content-Type'] = "application/json"
        self.client.post('/v1/transit/decrypt/test',
                         json={'ciphertext': data})


class TransitLocust(VaultLocust):
    task_set = TransitTasks
    weight = 1
    min_wait = 5000
    max_wait = 10000
