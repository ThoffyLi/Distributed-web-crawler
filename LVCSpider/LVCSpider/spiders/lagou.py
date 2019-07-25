# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
import pickle
import time
import os
from LVCSpider.items import TakeFirstLoader, LagouspiderItem
from scrapy import Request
from scrapy_redis.spiders import RedisCrawlSpider


class LagouSpider(RedisCrawlSpider):
    name = 'lagou'
    allowed_domains = ['lagou.com']
    redis_key = 'lagou:starturls'

    rules = (
        # example
          # allow=(r'jobs/\d+[.]html'), deny=(), allow_domains=(), deny_domains=(), restrict_xpaths=(),restrict_css=()
          #  tags=('a', 'area'), attrs=('href',)
        Rule(LinkExtractor(allow=('.*/zhaopin/.*',)), follow=True),
        Rule(LinkExtractor(allow=(r'.*/gongsi/.*')), follow=True),
        Rule(LinkExtractor(allow='.*jobs/\d+[.]html.*'), callback='parse_item', follow=True),

        Rule(LinkExtractor(deny=(r'.*m[.]lagou[.]com/.*')), follow=False),
        Rule(LinkExtractor(deny=(r'.*[.][kaiwu.lagou][.]com.*')), follow=False),
        Rule(LinkExtractor(deny=(r'.*[.][^lagou][.]com.*')), follow=False)
    )

    custom_settings = {
    "CONCURRENT_REQUESTS" : 1,
    "DOWNLOAD_DELAY" : 10,
    "DEPTH_PRIORITY":1
    }

    cookie_dict = dict()

    def make_requests_from_url(self, url):
 
        # cookie_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) +\
        #               "/cookies/" + self.name + ".cookie"
        #
        # cookies = pickle.load(open(cookie_path, "rb"))
        # # cookies is a list of dict
        #
        # for cookie in cookies:
        #     self.cookie_dict[cookie['name']] = cookie['value']

  
        from selenium import webdriver

        chrome_option = webdriver.ChromeOptions()

        chrome_option.add_argument("--disable-extensions")
        chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")


        browser = webdriver.Chrome(executable_path=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) +
                                "/chromedriver/chromedriver",chrome_options= chrome_option)
        browser.get(url)
        browser.find_element_by_css_selector(".lg_tbar_r > div > a:nth-child(1)").click()

        print("waiting")
        time.sleep(20)
  

        # get cookies
        time.sleep(5) #!!!!
        cookies = browser.get_cookies()
        cookie_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + \
                          "/cookies/" + self.name + ".cookie"
        pickle.dump(cookies, open(cookie_path,'wb'))

        # cookies is a list of dict
        for cookie in cookies:
            self.cookie_dict[cookie['name']] = cookie['value']

        return Request(url, dont_filter=True, cookies= self.cookie_dict)


    # customize each request for CrawlSpider
    def _build_request(self, rule, link):
        r = Request(url=link.url, callback=self._response_downloaded,cookies=self.cookie_dict)
        r.meta.update(rule=rule, link_text=link.text)
        return r


    def parse_item(self, response):

        item_loader = TakeFirstLoader(item = LagouspiderItem(), response = response)

        try:
            item_loader.add_css("content",".job-detail > *::text")
        except:
            item_loader.add_value("content", "N/A")

        item_loader.add_value("url", response.url)
        item_loader.add_css("location", ".job_request > h3 > span:nth-child(2)::text")
        item_loader.add_css("job_title",".job-name > h2::text")
        item_loader.add_css("company",".fl-cn::text")
        item_loader.add_css("salary",".job_request .salary::text")
        item_loader.add_css("education_req",".job_request > h3 > span:nth-child(4)::text")

        lagou_item = item_loader.load_item()
        yield lagou_item

