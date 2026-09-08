import pytest


@pytest.mark.parametrize('origin', ['https://hostile.example', 'null', 'http://localhost:9999', 'http://127.0.0.1:5173.attacker.example'])
def test_foreign_browser_cannot_mutate_project(client, origin):
    response = client.post('/api/projects', json={'profile': {}, 'basket': []}, headers={'Origin': origin})
    assert response.status_code == 403
    assert response.json()['code'] == 'forbidden'
    assert response.json()['request_id'] == response.headers['X-Request-ID']


def test_local_development_origin_and_cli_remain_supported(client):
    for headers in ({}, {'Origin': 'http://localhost:5173'}):
        response = client.post('/api/projects', json={'profile': {}, 'basket': []}, headers=headers)
        assert response.status_code == 200
