from fastapi import FastAPI
from pydantic import BaseModel
from redis.cluster import RedisCluster as Redis
from redis.cluster import ClusterNode

class Item(BaseModel):
    key: str

class Item_insert(BaseModel):
    key: str
    value: str

class Item_delete(BaseModel):
    key: str

app = FastAPI()

@app.post("/redis_insert/")
async def redis_insert(item_insert: Item_insert):
    key = item_insert.key
    value = item_insert.value
    nodes = [ClusterNode('redis-cluster', 7001)]
    rc = Redis(startup_nodes=nodes)
    rc.set(key, value)
    return key

@app.get("/redis_list/")
async def redis_list():
    nodes = [ClusterNode('redis-cluster', 7001)]
    rc = Redis(startup_nodes=nodes)
    json_str = rc.get("test").decode()
    return json_str

@app.delete("/redis_delete/")
async def redis_insert(Item_delete: Item_delete):
    key = Item_delete.key
    nodes = [ClusterNode('redis-cluster', 7001)]
    rc = Redis(startup_nodes=nodes)
    rc.delete(key)
    return key
