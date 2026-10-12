import os
import uuid
import pytest
import requests

BASE_URL = os.getenv('BASE_URL', 'https://compassuol.serverest.dev').rstrip('/')


def pytest_addoption(parser):
    parser.addoption('--run-live', action='store_true', default=False, help='Executa testes de integração reais na API')
    parser.addoption('--insecure-live', action='store_true', default=False,
                     help='Desabilita a verificação TLS nos testes live (somente workaround)')


def pytest_collection_modifyitems(config, items):
    if not config.getoption('--run-live'):
        skip = pytest.mark.skip(reason='Integração externa desativada: use --run-live')
        for item in items:
            if 'live' in item.keywords:
                item.add_marker(skip)


@pytest.fixture
def client(request):
    with requests.Session() as s:
        s.headers.update({'Accept': 'application/json'})
        s.verify = not request.config.getoption('--insecure-live')
        yield APIClient(s, BASE_URL)


class APIClient:
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url

    def request(self, method, path, **kwargs):
        if isinstance(self.session, requests.Session):
            kwargs.setdefault('verify', self.session.verify)
        return self.session.request(method, f'{self.base_url}{path}', timeout=15, **kwargs)

    def create_user(self, admin=False):
        email = f'qa.genai.{uuid.uuid4().hex}@example.org'
        user = {'nome': f'QA {uuid.uuid4().hex[:8]}', 'email': email,
                'password': 'QA!2026Abc', 'administrador': str(admin).lower()}
        res = self.request('POST', '/usuarios', json=user)
        assert res.status_code == 201, res.text
        return user, res.json()['_id']

    def login(self, user):
        res = self.request('POST', '/login', json={'email': user['email'], 'password': user['password']})
        assert res.status_code == 200, res.text
        token = res.json()['authorization']
        assert token.startswith('Bearer ')
        return {'Authorization': token}

    def create_product(self, headers, quantidade=10):
        product = {'nome': f'QA-PROD-{uuid.uuid4().hex}', 'preco': 125,
                   'descricao': 'Produto exclusivo de automacao', 'quantidade': quantidade}
        res = self.request('POST', '/produtos', json=product, headers=headers)
        assert res.status_code == 201, res.text
        return product, res.json()['_id']


@pytest.fixture
def admin(client):
    user, user_id = client.create_user(admin=True)
    headers = client.login(user)
    yield (user, user_id, headers)
    client.request('DELETE', f'/usuarios/{user_id}')


@pytest.fixture
def standard_user(client):
    user, user_id = client.create_user(admin=False)
    headers = client.login(user)
    yield (user, user_id, headers)
    client.request('DELETE', '/carrinhos/cancelar-compra', headers=headers)
    client.request('DELETE', f'/usuarios/{user_id}')


@pytest.fixture
def product(client, admin):
    _, _, h = admin
    data, prod_id = client.create_product(h)
    yield data, prod_id
    client.request('DELETE', f'/produtos/{prod_id}', headers=h)
