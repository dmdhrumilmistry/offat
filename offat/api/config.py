from fastapi import FastAPI
from redis import Redis
from rq import Queue, Worker

app = FastAPI(
    title='OFFAT - API'
)

redis_con = Redis(host='localhost', port=6379)
task_queue = Queue(name='offat_task_queue', connection=redis_con)
