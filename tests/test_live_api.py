"""Casos reais vinculados ao plano API-01..API-24 de Topic 1."""
import uuid
import pytest

pytestmark = pytest.mark.live


def test_api_01_login_valido(client, standard_user):
    u, _, _ = standard_user
    res = client.request('POST', '/login', json={'email': u['email'], 'password': u['password']})
    assert res.status_code == 200
    assert res.json()['authorization'].startswith('Bearer ')


def test_api_02_login_invalido(client, standard_user):
    u, _, _ = standard_user
    res = client.request('POST', '/login', json={'email': u['email'], 'password': 'senha-errada'})
    assert res.status_code == 401
    assert 'authorization' not in res.json()


@pytest.mark.parametrize('body', [{}, {'email': 'x'}, {'email': '', 'password': ''}])
def test_api_03_login_payload_invalido(client, body):
    res = client.request('POST', '/login', json=body)
    assert 400 <= res.status_code < 500, res.text


def test_api_04_usuario_criar_consultar(client):
    u, uid = client.create_user()
    try:
        res = client.request('GET', f'/usuarios/{uid}')
        assert res.status_code == 200
        assert res.json()['email'] == u['email']
    finally:
        client.request('DELETE', f'/usuarios/{uid}')


def test_api_05_email_duplicado(client, standard_user):
    u, _, _ = standard_user
    res = client.request('POST', '/usuarios', json=u)
    assert res.status_code == 400
    assert 'email' in res.json()['message'].lower()


def test_api_06_usuarios_listagem_filtro(client, standard_user):
    u, uid, _ = standard_user
    res = client.request('GET', '/usuarios', params={'email': u['email']})
    assert res.status_code == 200
    assert any(x['_id'] == uid for x in res.json()['usuarios'])


def test_api_07_usuario_put(client, standard_user):
    u, uid, _ = standard_user
    altered = {**u, 'nome': 'QA Nome Atualizado'}
    res = client.request('PUT', f'/usuarios/{uid}', json=altered)
    assert res.status_code == 200
    assert client.request('GET', f'/usuarios/{uid}').json()['nome'] == altered['nome']


def test_api_08_usuario_exclusao(client):
    _, uid = client.create_user()
    res = client.request('DELETE', f'/usuarios/{uid}')
    assert res.status_code == 200


def test_api_09_usuario_tipo_invalido(client):
    res = client.request('POST', '/usuarios', json={'nome': 123, 'email': 'invalido', 'password': [], 'administrador': True})
    assert res.status_code == 400


def test_api_10_produto_admin(client, admin, product):
    data, pid = product
    res = client.request('GET', f'/produtos/{pid}')
    assert res.status_code == 200
    assert res.json()['nome'] == data['nome']


@pytest.mark.parametrize('operation', ['POST', 'PUT', 'DELETE'])
def test_api_11_produto_sem_permissao(client, standard_user, product, operation):
    _, pid = product
    body = {'nome': f'QA-{uuid.uuid4().hex}', 'preco': 3, 'descricao': 'Teste', 'quantidade': 1}
    path = '/produtos' if operation == 'POST' else f'/produtos/{pid}'
    res = client.request(operation, path, json=body if operation != 'DELETE' else None, headers=standard_user[2])
    assert res.status_code == 403


def test_api_12_produto_duplicado(client, admin, product):
    body, _ = product
    res = client.request('POST', '/produtos', json=body, headers=admin[2])
    assert res.status_code == 400


def test_api_13_produto_filtros(client, product):
    p, pid = product
    res = client.request('GET', '/produtos', params={'nome': p['nome']})
    assert res.status_code == 200
    assert any(row['_id'] == pid for row in res.json()['produtos'])


def test_api_14_produto_put(client, admin, product):
    p, pid = product
    res = client.request('PUT', f'/produtos/{pid}', json={**p, 'preco': 140}, headers=admin[2])
    assert res.status_code == 200
    assert client.request('GET', f'/produtos/{pid}').json()['preco'] == 140


def test_api_15_produto_delete(client, admin):
    _, pid = client.create_product(admin[2])
    res = client.request('DELETE', f'/produtos/{pid}', headers=admin[2])
    assert res.status_code == 200


def test_api_16_carrinho_estoque_reduzido(client, standard_user, product):
    p, pid = product
    h = standard_user[2]
    res = client.request('POST', '/carrinhos', json={'produtos': [{'idProduto': pid, 'quantidade': 2}]}, headers=h)
    assert res.status_code == 201, res.text
    after = client.request('GET', f'/produtos/{pid}').json()
    assert after['quantidade'] == p['quantidade'] - 2
    assert client.request('DELETE', '/carrinhos/cancelar-compra', headers=h).status_code == 200


def test_api_17_carrinho_unico(client, standard_user, product):
    pid = product[1]
    h = standard_user[2]
    body = {'produtos': [{'idProduto': pid, 'quantidade': 1}]}
    assert client.request('POST', '/carrinhos', json=body, headers=h).status_code == 201
    res = client.request('POST', '/carrinhos', json=body, headers=h)
    assert res.status_code == 400
    assert client.request('DELETE', '/carrinhos/cancelar-compra', headers=h).status_code == 200


@pytest.mark.parametrize('id_produto,quantidade', [('NAO_EXISTE_123', 1), ('{product}', 999999)])
def test_api_18_carrinho_invalido(client, standard_user, product, id_produto, quantidade):
    pid = product[1] if id_produto == '{product}' else id_produto
    before = client.request('GET', f'/produtos/{product[1]}').json()['quantidade']
    res = client.request('POST', '/carrinhos', json={'produtos': [{'idProduto': pid, 'quantidade': quantidade}]}, headers=standard_user[2])
    assert res.status_code == 400
    assert client.request('GET', f'/produtos/{product[1]}').json()['quantidade'] == before


def test_api_19_concluir_sem_repor(client, standard_user, product):
    p, pid = product
    h = standard_user[2]
    assert client.request('POST', '/carrinhos', json={'produtos': [{'idProduto': pid, 'quantidade': 1}]}, headers=h).status_code == 201
    res = client.request('DELETE', '/carrinhos/concluir-compra', headers=h)
    assert res.status_code == 200
    assert client.request('GET', f'/produtos/{pid}').json()['quantidade'] == p['quantidade'] - 1


def test_api_20_cancelar_repor(client, standard_user, product):
    p, pid = product
    h = standard_user[2]
    assert client.request('POST', '/carrinhos', json={'produtos': [{'idProduto': pid, 'quantidade': 1}]}, headers=h).status_code == 201
    res = client.request('DELETE', '/carrinhos/cancelar-compra', headers=h)
    assert res.status_code == 200
    assert client.request('GET', f'/produtos/{pid}').json()['quantidade'] == p['quantidade']


@pytest.mark.parametrize('headers', [{}, {'Authorization': 'Bearer token-invalido'}])
def test_api_21_carrinho_sem_token(client, product, headers):
    pid = product[1]
    res = client.request('POST', '/carrinhos', json={'produtos': [{'idProduto': pid, 'quantidade': 1}]}, headers=headers)
    assert res.status_code == 401


def test_api_22_carrinhos_listar(client):
    res = client.request('GET', '/carrinhos')
    assert res.status_code == 200
    assert isinstance(res.json()['carrinhos'], list)


def test_api_23_produto_id_inexistente(client):
    res = client.request('GET', '/produtos/ID_INEXISTENTE_QA')
    assert res.status_code == 400


def test_api_24_carrinho_sem_compra(client, standard_user):
    res = client.request('DELETE', '/carrinhos/cancelar-compra', headers=standard_user[2])
    assert res.status_code == 200
    assert 'message' in res.json()
