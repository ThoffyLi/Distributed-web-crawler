from scrapy.cmdline import execute
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#choose the spider to run

execute(["scrapy", "crawl", "hupu"])
# execute(["scrapy", "crawl", "zhihu"])
# execute(["scrapy", "crawl", "lagou"])

