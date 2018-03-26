import sys
import os

import locust
from locust import task

sys.path.append(os.getcwd())
from locusts import VaultTaskSet, VaultLocust


class MysqlTasks(VaultTaskSet):
    CONFIG_NAME = 'test-mysql-local'
    ROLE_NAME = 'test-mysql-role'
    CONN_URL = 'root:abc123@tcp(vault0:3306)/mysql'
    CREATE_SQL = "CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}'; GRANT SELECT ON *.* TO '{{name}}'@'%';"

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
                         json={'plugin_name': 'mysql-database-plugin',
                               'allowed_roles': self.ROLE_NAME,
                               'connection_url': self.CONN_URL})

    def delete_connection(self):
        self.client.delete(f'/v1/database/config/{self.CONFIG_NAME}')

    def create_role(self):
        if self.is_in_list(self.ROLE_NAME, '/v1/database/roles'):
            self.delete_role()
        self.client.post(f'/v1/database/roles/{self.ROLE_NAME}',
                         json={'db_name': self.CONFIG_NAME,
                               'creation_statements': self.CREATE_SQL,
                               'default_ttl': '1h',
                               'max_ttl': '72h'})

    def delete_role(self):
        self.client.delete(f'/v1/database/roles/{self.ROLE_NAME}')

    @task
    def generate_creds(self):
        r = self.client.get(f'/v1/database/creds/{self.ROLE_NAME}')
        if 'lease_id' in r.json():
            lease_id = r.json()['lease_id']
            self.client.put('/v1/sys/leases/revoke',
                            json={'lease_id': lease_id})


class MysqlLocust(VaultLocust):
    task_set = MysqlTasks
    weight = 1
    min_wait = 5000
    max_wait = 10000
