from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from bson import ObjectId

from database import products_collection
from models import Product


app = FastAPI(
    title="Ecommerce Product API",
    description="Simple FastAPI + MongoDB ecommerce project",
    version="1.0"
)


templates = Jinja2Templates(directory="templates")


def serialize_product(product):
    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "price": product["price"],
        "category": product["category"],
        "stock": product["stock"]
    }


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


@app.get("/api/products")
def get_products():

    products = []

    for product in products_collection.find():
        products.append(serialize_product(product))

    return products


@app.get("/api/products/{product_id}")
def get_product(product_id: str):

    try:
        object_id = ObjectId(product_id)

    except:
        raise HTTPException(
            status_code=400,
            detail="Invalid product ID"
        )

    product = products_collection.find_one(
        {"_id": object_id}
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return serialize_product(product)


@app.post("/api/products")
def create_product(product: Product):

    product_data = product.model_dump()

    result = products_collection.insert_one(
        product_data
    )

    new_product = products_collection.find_one(
        {"_id": result.inserted_id}
    )

    return serialize_product(new_product)


@app.put("/api/products/{product_id}")
def update_product(
    product_id: str,
    product: Product
):

    try:
        object_id = ObjectId(product_id)

    except:
        raise HTTPException(
            status_code=400,
            detail="Invalid product ID"
        )

    result = products_collection.update_one(
        {"_id": object_id},
        {
            "$set": product.model_dump()
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    updated_product = products_collection.find_one(
        {"_id": object_id}
    )

    return serialize_product(updated_product)


@app.delete("/api/products/{product_id}")
def delete_product(product_id: str):

    try:
        object_id = ObjectId(product_id)

    except:
        raise HTTPException(
            status_code=400,
            detail="Invalid product ID"
        )

    result = products_collection.delete_one(
        {"_id": object_id}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return {
        "message": "Product deleted successfully"
    }