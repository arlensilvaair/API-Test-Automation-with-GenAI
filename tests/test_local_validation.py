"""Testes offline de componentes da suíte; NÃO substituem testes reais de integração."""
from unittest.mock import Mock
from conftest import APIClient


def response(status, data):
    r = Mock(status_code=status)
    r.json.return_value = data
    r.text = repr(data)
    return r


def test_client_url_timeout():
    session = Mock()
    session.request.return_value = response(200, {})
    c = APIClient(session, 'https://example.test')
    c.request('GET', '/produtos', params={'nome': 'A'})
    session.request.assert_called_once_with('GET', 'https://example.test/produtos', timeout=15, params={'nome': 'A'})


def test_user_payload_and_unique_email():
    session = Mock()
    session.request.side_effect = [response(201, {'_id': 'id1'}), response(201, {'_id': 'id2'})]
    c = APIClient(session, 'https://example.test')
    a, _ = c.create_user()
    b, _ = c.create_user()
    assert a['email'] != b['email']
    assert a['administrador'] == b['administrador'] == 'false'


def test_login_bearer():
    session = Mock()
    session.request.return_value = response(200, {'authorization': 'Bearer abc'})
    c = APIClient(session, 'https://example.test')
    assert c.login({'email': 'u@example.org', 'password': '123'}) == {'Authorization': 'Bearer abc'}


def test_login_rejeita_token_sem_bearer():
    session = Mock()
    session.request.return_value = response(200, {'authorization': 'abc'})
    c = APIClient(session, 'https://example.test')
    try:
        c.login({'email': 'u@example.org', 'password': '123'})
    except AssertionError:
        pass
    else:
        raise AssertionError('Deveria rejeitar token sem Bearer')


def test_produto_payload_quantidade():
    session = Mock()
    session.request.return_value = response(201, {'_id': 'p1'})
    c = APIClient(session, 'https://example.test')
    p, pid = c.create_product({'Authorization': 'Bearer abc'}, quantidade=9)
    assert pid == 'p1' and p['quantidade'] == 9
    assert p['nome'].startswith('QA-PROD-')


def test_cadastro_falha_visivel():
    session = Mock()
    session.request.return_value = response(400, {'message': 'Erro'})
    c = APIClient(session, 'https://example.test')
    try:
        c.create_user()
    except AssertionError:
        pass
    else:
        raise AssertionError('Falha não foi sinalizada')
