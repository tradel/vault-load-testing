from locust import TaskSet

import sys
import os
import json

sys.path.append(os.getcwd())
import common


class VaultLoadTaskSet(TaskSet):

    def on_start(self):
        with open('testdata.json', 'r') as f:
            setattr(self, 'testdata', json.load(f))
        self.client.headers['X-Vault-Token'] = self.testdata['token']
