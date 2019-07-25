# This is the script to push start urls into Redis
# Used independently outside the project
import redis
import time

HOST = ""
PORT = 6379

conn = redis.Redis(host = HOST, port = PORT)

while(True):
    conn.lpush("hupu:starturls","https://bbs.hupu.com/bxj")
    conn.lpush("zhihu:starturls", "https://www.zhihu.com/signin")
    conn.lpush("lagou:starturls", "https://www.lagou.com")
    time.sleep(5)




