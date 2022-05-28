import argparse
from collections import defaultdict
import uuid
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, Request, Response, status
from pydantic import BaseModel, EmailStr

from time import sleep

from threading import RLock

from smtp_client import send_mail

SLEEP_TIME = 10

app = FastAPI()

items = {}
users = {}
tokens = {}
ips = {}
action_ids = defaultdict(lambda: 0)

lock = RLock()

def send_email(user: str):
    send_mail(user, "welcome to our service again!")
    return

def send_email_task(user: str, action_id: int):
    sleep(10)
    lock.acquire()
    if action_id == action_ids[user]:
        send_email(user)
        del action_ids[user]
    lock.release()

def no_token(ip: str, background_tasks: BackgroundTasks):
    if ip not in ips:
        return
    name = ips[ip]
    lock.acquire()
    action_ids[name] = action_ids[name] + 1 
    action_id = action_ids[name]
    lock.release()
    background_tasks.add_task(send_email_task, name, action_id)
    return

class Item(BaseModel):
    name: Optional[str]
    description: Optional[str]
    image: Optional[str]

class User(BaseModel):
    name: EmailStr
    password: str

@app.get("/items/get_item")
def read_item(item_id: str, background_tasks: BackgroundTasks, request: Request, token: Optional[str] = None):
    if token is None:
        ip = request.client.host
        no_token(ip, background_tasks)
    if item_id in items:
        return items[item_id]
    return None


@app.get("/items")
def read_items(background_tasks: BackgroundTasks, request: Request, token: Optional[str] = None):
    if token is None:
        ip = request.client.host
        no_token(ip, background_tasks)
    has_token = token in list(tokens.values())
    return [(v, k) for v, k in items.items() if "locked" not in k.description or has_token]

def _create_item(item: Item):
    new_id = uuid.uuid1()
    items[str(new_id)] = item
    return {"item": item, "id": str(new_id)}

@app.post("/items")
async def create_item(item: Item):
    return _create_item(item)

@app.put("/items")
async def change_item(item_id: str, item: Item):
    if item_id not in items:
        return None
    old_item = items[item_id]
    if item.name is not None:
        old_item.name = item.name
    if item.description is not None:
        old_item.description = item.description
    if item.image is not None:
        old_item.image = item.image

    return old_item


@app.delete("/items")
async def delete_item(item_id: str):
    if item_id in items:
        del items[item_id]

@app.post("/register")
async def register_user(user: User, request: Request):
    if user.name in users:
        return "User exists"
    ip = request.client.host
    users[user.name] = user
    ips[ip] = user.name

@app.get("/login", status_code=status.HTTP_200_OK)
async def login(user: User, response: Response):
    if user.name not in users:
        response.status_code = status.HTTP_403_FORBIDDEN
        return "Wrong username"
    acc = users[user.name]
    if acc.password != user.password:
        response.status_code = status.HTTP_403_FORBIDDEN
        return "Wrong password"

    tokens[user.name] = str(uuid.uuid1())
    return tokens[user.name]
    
_create_item(Item(name="hah 1", description="locked",image=None))
_create_item(Item(name="hah 2", description="normal item",image=None))