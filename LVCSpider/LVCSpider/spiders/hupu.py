# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from scrapy_redis.spiders import RedisSpider
from LVCSpider.items import HpspiderItem, TakeFirstLoader


class HupuSpider(RedisSpider):
    name = 'hupu'
    allowed_domains = ['bbs.hupu.com']
    # start_urls = ['https://bbs.hupu.com/bxj']
    page = 1
    redis_key = 'hupu:starturls'

    base_url = "https://bbs.hupu.com"

    custom_settings = {
        "COOKIES_ENABLED" : False,
        "COOKIES_DEBUG" : False,
        "AUTOTHROTTLE_ENABLED" : False,
        "DOWNLOAD_DELAY" : 0
    }

    # input in Redis-client: lpush hupu:starturls https://bbs.hupu.com/bxj
    def parse(self, response):
        post_nodes = response.css("#ajaxtable > div.show-list > ul > li")
        for post_node in post_nodes:
            create_date = post_node.css("li > div.author > a:nth-child(3)::text").extract_first()
            reply_num = post_node.css("li > span:nth-child(3)::text").extract_first()
            views = post_node.css("li > span:nth-child(3)::text").extract_first()
            post_url = post_node.css("li > div.titlelink > a::attr(href)").extract_first()

            yield Request(url=urljoin(response.url, post_url),
                          meta={"create_date": create_date, "reply_num": reply_num,
                                "views": views, "page": self.page, "url":urljoin(self.base_url, post_url)},
                          callback=self.parse_details)

        self.page = self.page + 1
        next_url = "https://bbs.hupu.com/bxj-" + str(self.page)
        yield Request(url=next_url, callback=self.parse)

    def parse_details(self, response):
        item_loader = TakeFirstLoader(item=HpspiderItem(), response=response)



        item_loader.add_css("title", "#t_main > div.bbs_head > div.bbs-hd-h1 > h1::text")
        item_loader.add_css("author_level",
                            "#tpc > div > div.floor_box > div.author > div.left > span:nth-child(2) > a::text")
        item_loader.add_css("create_time",
                            "#tpc > div > div.floor_box > div.author > div.left > span:nth-child(4)::text")
        item_loader.add_css("author_id", "#tpc > div > div.floor_box > div.author > div.left > a.u::text")
        item_loader.add_css("Liangs", "#t_main > div.bbs_head > div.bbs-hd-h1 > span.browse > span:nth-child(2)::text")

        item_loader.add_value("url", response.meta.get("url"))
        item_loader.add_value("create_date", response.meta.get("create_date"))
        item_loader.add_value("reply_num", response.meta.get("reply_num"))
        item_loader.add_value("views", response.meta.get("views"))
        item_loader.add_value("page", response.meta.get("page"))

        hp_item = item_loader.load_item()

        yield hp_item
