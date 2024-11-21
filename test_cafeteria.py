#pytest test_cafeteria.py

import pytest
from fastapi.testclient import TestClient
from cafeteria import app, cardapio, pedidos

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_e_teardown():
    # Limpa os bancos de dados simulados antes de cada teste
    cardapio.clear()
    pedidos.clear()


def test_adicionar_produto():
    produto = {"nome": "Café", "preco": 5.0, "marca": "Cafeteria X"}
    response = client.post("/produto/1", json=produto)
    assert response.status_code == 200
    assert response.json() == produto


def test_adicionar_produto_com_id_duplicado():
    produto = {"nome": "Café", "preco": 5.0, "marca": "Cafeteria X"}
    client.post("/produto/1", json=produto)
    response = client.post("/produto/1", json=produto)
    assert response.status_code == 400
    assert response.json() == {"detail": "ID do produto já existe"}


def test_consultar_produto():
    produto = {"nome": "Café", "preco": 5.0, "marca": "Cafeteria X"}
    client.post("/produto/1", json=produto)
    response = client.get("/produto/1")
    assert response.status_code == 200
    assert response.json() == produto


def test_consultar_produto_inexistente():
    response = client.get("/produto/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Produto não encontrado"}


def test_atualizar_produto():
    produto = {"nome": "Café", "preco": 5.0, "marca": "Cafeteria X"}
    client.post("/produto/1", json=produto)
    atualizacao = {"preco": 6.0}
    response = client.patch("/produto/1", json=atualizacao)
    assert response.status_code == 200
    assert response.json()["preco"] == 6.0


def test_remover_produto_com_autenticacao():
    produto = {"nome": "Café", "preco": 5.0, "marca": "Cafeteria X"}
    client.post("/produto/1", json=produto)
    response = client.delete(
        "/produto/1", auth=("admin", "4321")
    )
    assert response.status_code == 200
    assert response.json() == {"Sucesso": "Produto removido!"}


def test_remover_produto_sem_autenticacao():
    produto = {"nome": "Café", "preco": 5.0, "marca": "Cafeteria X"}
    client.post("/produto/1", json=produto)
    response = client.delete("/produto/1")
    assert response.status_code == 401

def test_adicionar_pedido():
    produto = {"nome": "Café", "preco": 5.0, "marca": "Cafeteria X"}
    client.post("/produto/1", json=produto)
    pedido = {"produtos": [1], "total": 0.0}
    response = client.post("/pedido/1", json=pedido)
    assert response.status_code == 200
    assert response.json()["total"] == 5.0


def test_adicionar_pedido_com_produto_inexistente():
    pedido = {"produtos": [999], "total": 0.0}
    response = client.post("/pedido/1", json=pedido)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Os seguintes produtos não existem no cardápio: [999]"
    }


def test_consultar_pedido():
    produto = {"nome": "Café", "preco": 5.0, "marca": "Cafeteria X"}
    client.post("/produto/1", json=produto)
    pedido = {"produtos": [1], "total": 0.0}
    client.post("/pedido/1", json=pedido)
    response = client.get("/pedido/1")
    assert response.status_code == 200
    assert response.json()["total"] == 5.0


def test_remover_pedido_com_autenticacao():
    produto = {"nome": "Café", "preco": 5.0, "marca": "Cafeteria X"}
    client.post("/produto/1", json=produto)
    pedido = {"produtos": [1], "total": 0.0}
    client.post("/pedido/1", json=pedido)
    response = client.delete(
        "/pedido/1", auth=("admin", "4321")
    )
    assert response.status_code == 200
    assert response.json() == {"Sucesso": "Pedido removido!"}


def test_remover_pedido_sem_autenticacao():
    produto = {"nome": "Café", "preco": 5.0, "marca": "Cafeteria X"}
    client.post("/produto/1", json=produto)
    pedido = {"produtos": [1], "total": 0.0}
    client.post("/pedido/1", json=pedido)
    response = client.delete("/pedido/1")
    assert response.status_code == 401
