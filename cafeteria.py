from fastapi import FastAPI, Path, Query, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional, List
from pydantic import BaseModel, ValidationError
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

security = HTTPBasic()

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

@app.exception_handler(Exception)
async def excecao_generica_handler(request: Request, exc: Exception):
    logger.error(f"Erro inesperado: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ocorreu um erro inesperado. Tente novamente mais tarde."}
    )

@app.exception_handler(ValidationError)
async def validacao_handler(request: Request, exc: ValidationError):
    logger.warning(f"Erro de validação: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.info(f"HTTP Exception: {exc.detail} (status code: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.post("/produto/{produto_id}", response_model=Produto)
def adicionar_produto(produto_id: int, produto: Produto):
    if produto_id in cardapio:
        raise HTTPException(status_code=400, detail="ID do produto já existe")
    cardapio[produto_id] = produto.model_dump()
    logger.info(f"Produto adicionado: {produto}")
    return cardapio[produto_id]

@app.get("/produto/{produto_id}", response_model=Produto)
def consultar_produto(produto_id: int = Path(..., description="ID do produto a ser consultado", gt=0)):
    if produto_id not in cardapio:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return cardapio[produto_id]

@app.patch("/produto/{produto_id}", response_model=Produto)
def atualizar_produto(produto_id: int, produto: AtualizaProduto):
    if produto_id not in cardapio:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    produto_existente = cardapio[produto_id]
    produto_existente.update({k: v for k, v in produto.model_dump().items() if v is not None})
    logger.info(f"Produto atualizado: {produto_existente}")
    return produto_existente

@app.delete("/produto/{produto_id}", dependencies=[Depends(verificar_usuario)])
def remover_produto(produto_id: int):
    if produto_id not in cardapio:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    del cardapio[produto_id]
    logger.info(f"Produto removido: ID {produto_id}")
    return {"Sucesso": "Produto removido!"}

@app.get("/produtos/")
def listar_produtos(
    nome: Optional[str] = Query(None, description="Filtrar produtos pelo nome"),
    marca: Optional[str] = Query(None, description="Filtrar produtos pela marca"),
    ordenacao: Optional[str] = Query(None, description="Ordenar por 'nome' ou 'preco'")
):
    produtos = list(cardapio.values())
    if nome:
        produtos = [produto for produto in produtos if produto["nome"].lower() == nome.lower()]
    if marca:
        produtos = [produto for produto in produtos if produto.get("marca", "").lower() == marca.lower()]
    if ordenacao:
        if ordenacao not in {"nome", "preco"}:
            raise HTTPException(status_code=400, detail="Ordenação inválida. Use 'nome' ou 'preco'.")
        produtos.sort(key=lambda x: x[ordenacao])
    return produtos


@app.post("/pedido/{pedido_id}", response_model=Pedido)
def adicionar_pedido(pedido_id: int, pedido: Pedido):
    if pedido_id in pedidos:
        raise HTTPException(status_code=400, detail="ID do pedido já existe")

    ids_inexistentes = [produto_id for produto_id in pedido.produtos if produto_id not in cardapio]
    if ids_inexistentes:
        raise HTTPException(
            status_code=404,
            detail=f"Os seguintes produtos não existem no cardápio: {ids_inexistentes}"
        )

    total = sum([cardapio[produto_id]["preco"] for produto_id in pedido.produtos]) 
    
    pedido.total = total
    pedidos[pedido_id] = pedido.model_dump()
    logger.info(f"Pedido adicionado: {pedido}")
    return pedidos[pedido_id]

@app.get("/pedido/{pedido_id}", response_model=Pedido)
def consultar_pedido(pedido_id: int):
    if pedido_id not in pedidos:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedidos[pedido_id]

@app.delete("/pedido/{pedido_id}", dependencies=[Depends(verificar_usuario)])
def remover_pedido(pedido_id: int):
    if pedido_id not in pedidos:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    del pedidos[pedido_id]
    logger.info(f"Pedido removido: ID {pedido_id}")
    return {"Sucesso": "Pedido removido!"}
