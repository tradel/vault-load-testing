import sys
import os

from locust import task

sys.path.append(os.getcwd())
from locusts import VaultTaskSet, VaultLocust


class MongoDbTasks(VaultTaskSet):
    CONFIG_NAME = 'test-mongodb-local'
    ROLE_NAME = 'test-mongodb-role'
    CONN_URL = 'mongodb://vault0:27017/admin'
    CREATE_SQL = '{"db": "admin", "roles": [{"role": "read", "db": "foo"}]}'

    def setup(self):
        self.mount('database')
        self.create_connection()
        self.create_role()

    def teardown(self):
        self.delete_role()
        self.delete_connection()

    def create_connection(self):
        if self.is_in_list(self.CONFIG_NAME, '/v1/database/config'):
            self.delete_connection()
        self.client.post(f'/v1/database/config/{self.CONFIG_NAME}',
                         json={'plugin_name': 'mongodb-database-plugin',
                               'allowed_roles': self.ROLE_NAME,
                               'connection_url': self.CONN_URL})

    def create_role(self):
        if self.is_in_list(self.ROLE_NAME, '/v1/database/roles'):
            self.delete_role()
        self.client.post(f'/v1/database/roles/{self.ROLE_NAME}',
                         json={'db_name': self.CONFIG_NAME,
                               'creation_statements': self.CREATE_SQL,
                               'default_ttl': '1h',
                               'max_ttl': '72h'})

    def delete_connection(self):
        self.client.delete(f'/v1/database/config/{self.CONFIG_NAME}')

    def delete_role(self):
        self.client.delete(f'/v1/database/roles/{self.ROLE_NAME}')

    @task
    def generate_creds(self):
        r = self.client.get(f'/v1/database/creds/{self.ROLE_NAME}')
        lease_id = r.json()['lease_id']
        self.client.put('/v1/sys/leases/revoke',
                        json={'lease_id': lease_id})


class MongoDbLocust(VaultLocust):
    task_set = MongoDbTasks
    weight = 1
    min_wait = 5000
    max_wait = 10000
