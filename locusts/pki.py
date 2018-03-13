import json
import sys

import base64
import os

from locust import HttpLocust, task
from locust.clients import HttpSession

sys.path.append(os.getcwd())
import common
from locusts import VaultLoadTaskSet


class PkiTasks(VaultLoadTaskSet):

    def on_start(self):
        super().on_start()
        c = self.client  # type: HttpSession
        with c.post('/v1/sys/mounts/pki',
                    json={'type': 'pki'},
                    catch_response=True) as response:
            response.success()
        with c.post('/v1/pki/root/generate/internal',
                    json={'common_name': 'example.com', 'ttl': '8760h'},
                    catch_response=True) as response:
            response.success()
        with c.post('/v1/pki/roles/pki-test-role',
                    json={'allowed_domains': 'example.com', 'max_ttl': '72h', 'allow_subdomains': True},
                    catch_response=True) as response:
            response.success()

    @task
    def generate_cert(self):
        c = self.client  # type: HttpSession
        c.post('/v1/pki/issue/pki-test-role',
               json={'common_name': 'foo.example.com'})


class PkiLocust(HttpLocust):
    task_set = PkiTasks
    weight = 1
    min_wait = 5000
    max_wait = 10000
