import mmh3
import redis
import math
import time
from LVCSpider.settings import REDIS_HOST

class PyBloomFilter():
    # Set 100 random seeds
    SEEDS = [543, 460, 171, 876, 796, 607, 650, 81, 837, 545, 591, 946, 846, 521, 913, 636, 878, 735, 414, 372,
             344, 324, 223, 180, 327, 891, 798, 933, 493, 293, 836, 10, 6, 544, 924, 849, 438, 41, 862, 648, 338,
             465, 562, 693, 979, 52, 763, 103, 387, 374, 349, 94, 384, 680, 574, 480, 307, 580, 71, 535, 300, 53,
             481, 519, 644, 219, 686, 236, 424, 326, 244, 212, 909, 202, 951, 56, 812, 901, 926, 250, 507, 739, 371,
             63, 584, 154, 7, 284, 617, 332, 472, 140, 605, 262, 355, 526, 647, 923, 199, 518]

    def __init__(self, capacity=10000000, error_rate=0.1, conn=None, key='BloomFilter'):
        self.m = math.ceil(capacity*math.log2(math.e)*math.log2(1/error_rate))      #total bits required
        self.k = math.ceil(math.log1p(2)*self.m/capacity)                           #hash
        self.mem = math.ceil(self.m/8/1024/1024)                                    #cache
        self.blocknum = math.ceil(self.mem/512)                                     #256M blocks
        self.seeds = self.SEEDS[0:self.k]
        self.key = key
        self.N = 2**31-1
        self.redis = conn
        print(self.mem)
        print(self.k)

    def add(self, value):
        name = self.key + "_" + str(ord(value[0])%self.blocknum)
        hashs = self.get_hashs(value)
        for hash in hashs:
            self.redis.setbit(name, hash, 1)

    def is_exist(self, value):
        name = self.key + "_" + str(ord(value[0])%self.blocknum)
        hashs = self.get_hashs(value)
        exist = True
        for hash in hashs:
            exist = exist & self.redis.getbit(name, hash)
        return exist

    def get_hashs(self, value):
        hashs = list()
        for seed in self.seeds:
            hash = mmh3.hash(value, seed)
            if hash >= 0:
                hashs.append(hash)
            else:
                hashs.append(self.N - hash)
        return hashs


pool = redis.ConnectionPool(host=REDIS_HOST, port=6379, db=0)
conn = redis.StrictRedis(connection_pool=pool)

#start = time.time()
#bf = PyBloomFilter(conn=conn)
#bf.add('www.jobbole.com')
#bf.add('www.zhihu.com')
#print(bf.is_exist('www.zhihu.com'))
#print(bf.is_exist('www.lagou.com'))