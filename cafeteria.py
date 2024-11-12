from fastapi import FastAPI, Path, Query, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional, List
from pydantic import BaseModel
import logging

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Segurança básica para endpoints destrutivos
security = HTTPBasic()

# Banco de dados simulado
cardapio = {}
pedidos = {}

# Autenticação simples (para fins de exemplo)
def verificar_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != "4321":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

# Classes de Modelos
class Produto(BaseModel):
    nome: str
    preco: float
    marca: Optional[str] = None

class AtualizaProduto(BaseModel):
    nome: Optional[str] = None
    preco: Optional[float] = None
    marca: Optional[str] = None

class Pedido(BaseModel):
    produtos: List[int]  # IDs dos produtos no pedido
    total: float

# Endpoints de Produto
@app.post("/adicionar-produto/{produto_id}", response_model=Produto)
def adicionar_produto(produto_id: int, produto: Produto):
    if produto_id in cardapio:
        raise HTTPException(status_code=400, detail="ID do produto já existe")
    cardapio[produto_id] = produto.dict()
    logger.info(f"Produto adicionado: {produto}")
    return cardapio[produto_id]

@app.get("/consultar-produto/{produto_id}", response_model=Produto)
def consultar_produto(produto_id: int = Path(..., description="ID do produto a ser consultado", gt=0)):
    if produto_id not in cardapio:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return cardapio[produto_id]

@app.put("/atualizar-produto/{produto_id}", response_model=Produto)
def atualizar_produto(produto_id: int, produto: AtualizaProduto):
    if produto_id not in cardapio:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    produto_existente = cardapio[produto_id]
    produto_existente.update({k: v for k, v in produto.dict().items() if v is not None})
    logger.info(f"Produto atualizado: {produto_existente}")
    return produto_existente

@app.delete("/remover-produto/{produto_id}", dependencies=[Depends(verificar_usuario)])
def remover_produto(produto_id: int):
    if produto_id not in cardapio:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    del cardapio[produto_id]
    logger.info(f"Produto removido: ID {produto_id}")
    return {"Sucesso": "Produto removido!"}

# Filtro e ordenação de produtos
@app.get("/produtos/")
def listar_produtos(nome: Optional[str] = Query(None)):
    produtos = list(cardapio.values())
    if nome:
        produtos = [produto for produto in produtos if produto["nome"] == nome]
    return produtos


# Endpoints de Pedido
@app.post("/adicionar-pedido/{pedido_id}", response_model=Pedido)
def adicionar_pedido(pedido_id: int, pedido: Pedido):
    if pedido_id in pedidos:
        raise HTTPException(status_code=400, detail="ID do pedido já existe")
    
    total = sum([cardapio[produto_id]["preco"] for produto_id in pedido.produtos if produto_id in cardapio])
    pedido.total = total
    pedidos[pedido_id] = pedido.dict()
    logger.info(f"Pedido adicionado: {pedido}")
    return pedidos[pedido_id]

@app.get("/consultar-pedido/{pedido_id}", response_model=Pedido)
def consultar_pedido(pedido_id: int):
    if pedido_id not in pedidos:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedidos[pedido_id]

@app.delete("/remover-pedido/{pedido_id}", dependencies=[Depends(verificar_usuario)])
def remover_pedido(pedido_id: int):
    if pedido_id not in pedidos:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    del pedidos[pedido_id]
    logger.info(f"Pedido removido: ID {pedido_id}")
    return {"Sucesso": "Pedido removido!"}
