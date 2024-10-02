from fastapi import FastAPI
from pydantic import BaseModel
from redis.cluster import RedisCluster as Redis
from redis.cluster import ClusterNode

app = FastAPI()

@app.get("/redis_insert/")
async def redis_insert():
    key = "test"
    value = 200
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