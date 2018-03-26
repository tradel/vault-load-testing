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

    def setup(self):
        self.mount('transit')

    @task
    def encrypt_block(self):
        data = common.random_data(self.locust.testdata['transit_size'])
        data = base64.b64encode(data.encode()).decode()
        self.client.post('/v1/transit/encrypt/test', json={'plaintext': data})


class TransitLocust(VaultLocust):
    task_set = TransitTasks
    weight = 1
    min_wait = 5000
    max_wait = 10000
