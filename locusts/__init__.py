from locust import TaskSet, HttpLocust
from locust.clients import ResponseContextManager, HttpSession, RequestException, events, CatchResponseError
import time

import json


class VaultLocust(HttpLocust):

    token = None
    testdata = None

    def __init__(self):
        super().__init__()
        self.client = VaultSession(base_url=self.host)

    def setup(self):
        with open('testdata.json', 'r') as f:
            config = json.load(f)
            self._set_testdata(config)
            self._set_token(config['token'])

    @classmethod
    def _set_token(cls, token):
        cls.token = token

    @classmethod
    def _set_testdata(cls, data):
        cls.testdata = data


class VaultTaskSet(TaskSet):

    def mount(self, name: str, mount_point: str=None):
        mount_point = mount_point or name
        r = self.client.get('/v1/sys/mounts')
        if f'{mount_point}/' not in r.json():
            self.client.post(f'/v1/sys/mounts/{mount_point}', json={'type': name})

    def enable_auth(self, name: str, path: str=None):
        path = path or name
        r = self.client.get('/v1/sys/auth')
        if f'{path}/' not in r.json():
            self.client.post(f'/v1/sys/auth/{path}', json={'type': name})

    def revoke_lease(self, lease_id: str):
        self.client.put('/v1/sys/leases/revoke',
                        json={'lease_id': lease_id})

    def is_in_list(self, key: str, uri: str) -> bool:
        with self.client.request('LIST', uri, catch_response=True) as r:
            if r.status_code == 404:
                r.success()
                return False
            else:
                return key in r.json()['data']['keys']

    @property
    def client(self) -> HttpSession:
        client = super().client  # type: HttpSession
        client.headers['X-Vault-Token'] = self.locust.token
        return client


class VaultSession(HttpSession):

    def request(self, method, url, name=None, catch_response=False, **kwargs):

        # prepend url with hostname unless it's already an absolute URL
        url = self._build_url(url)

        # store meta data that is used when reporting the request to locust's statistics
        request_meta = dict()

        # set up pre_request hook for attaching meta data to the request object
        request_meta["method"] = method
        request_meta["start_time"] = time.time()

        response = self._send_request_safe_mode(method, url, **kwargs)

        # record the consumed time
        request_meta["response_time"] = int((time.time() - request_meta["start_time"]) * 1000)

        request_meta["name"] = name or (response.history and response.history[0] or response).request.path_url

        # get the length of the content, but if the argument stream is set to True, we take
        # the size from the content-length header, in order to not trigger fetching of the body
        if kwargs.get("stream", False):
            request_meta["content_size"] = int(response.headers.get("content-length") or 0)
        else:
            request_meta["content_size"] = len(response.content or "")

        if catch_response:
            response.locust_request_meta = request_meta
            return ResponseContextManager(response)
        else:
            try:
                response.raise_for_status()
            except RequestException as e:
                try:
                    e = CatchResponseError('. '.join(response.json()['errors']))
                except KeyError:
                    pass

                events.request_failure.fire(
                    request_type=request_meta["method"],
                    name=request_meta["name"],
                    response_time=request_meta["response_time"],
                    exception=e,
                )
            else:
                events.request_success.fire(
                    request_type=request_meta["method"],
                    name=request_meta["name"],
                    response_time=request_meta["response_time"],
                    response_length=request_meta["content_size"],
                )
            return response
