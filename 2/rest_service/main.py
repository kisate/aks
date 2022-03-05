import uuid
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

items = {}


class Item(BaseModel):
    name: Optional[str]
    description: Optional[str]
    image_url: Optional[str]


@app.get("/items/get_item")
def read_item(item_id: str):
    if item_id in items:
        return items[item_id]
    return None


@app.get("/items")
def read_items():
    return items


@app.post("/items")
async def create_item(item: Item):
    new_id = uuid.uuid1()
    items[str(new_id)] = item
    return {"item": item, "id": str(new_id)}


@app.put("/items")
async def change_item(item_id: str, item: Item):
    if item_id not in items:
        return None
    old_item = items[item_id]
    if item.name is not None:
        old_item.name = item.name
    if item.description is not None:
        old_item.description = item.description

    return old_item


@app.delete("/items")
async def delete_item(item_id: str):
    if item_id in items:
        del items[item_id]
