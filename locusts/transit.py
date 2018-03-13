import json
import sys

import base64
import os

from locust import HttpLocust, task
from locust.clients import HttpSession

sys.path.append(os.getcwd())
import common
from locusts import VaultLoadTaskSet


class TransitTasks(VaultLoadTaskSet):

    def on_start(self):
        super().on_start()
        with self.client.post('/v1/sys/mounts/transit',
                              json={'type': 'transit'},
                              catch_response=True) as response:
            response.success()

    @task
    def encrypt_block(self):
        data = common.random_data(self.testdata['transit_size'])
        data = base64.b64encode(data.encode()).decode()
        self.client.post('/v1/transit/encrypt/foo',
                         json={'plaintext': data})


class TransitLocust(HttpLocust):
    task_set = TransitTasks
    weight = 1
    min_wait = 5000
    max_wait = 10000
