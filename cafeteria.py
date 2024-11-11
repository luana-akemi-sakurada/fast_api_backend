from fastapi import FastAPI, Path
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

class Product(BaseModel):
    name: str
    price: float
    quantity: int

inventory = {
}

@app.get("/get-product/{product_id}")
def get_product(product_id: int = Path(description = "The ID of the product", gt=0)):
    return inventory[product_id]

@app.get("/get-by-name")
def get_product(name: str = Query(None, title = "The name of the product", description = "The Name of the product")):
    for product_id in inventory:
        if inventory[product_id].name == name:
            return inventory[product_id]
    return {"Data": "Product not found"}

@app.post("/create-product/{product_id}")
def create_product(product_id: int, product: Product):
    if product_id in inventory:
        return {"Error": "Product already exists"}
    inventory[product_id] = product
    return inventory[product_id]