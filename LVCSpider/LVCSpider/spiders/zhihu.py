# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
import time
import pickle
import json
import re
from urllib import parse
from scrapy.loader import ItemLoader
from LVCSpider.items import ZhihuQuestionItem,ZhihuAnswerItem
from scrapy_redis.spiders import RedisSpider
import datetime
import os

class ZhihuSpider(RedisSpider):
    name = 'zhihu'
    allowed_domains = ['zhihu.com']
    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://zhihu.com",
        "User-Agent": ""
    }

    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 3,
        "DEPTH_PRIORITY": -1
    }

    redis_key = 'zhihu:starturls'

    zhihu_start_url = "https://www.zhihu.com/api/v3/feed/topstory/recommend?session_token=24b41b6797d654483c2e4906cca06475&desktop=true&page_number={0}&limit={1}&action=down&after_id=11"

    answer_start_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2C" \
                       "annotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_sett" \
                       "ings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2C" \
                       "is_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D." \
                       "topics&limit={1}&offset={2}&platform=desktop&sort_by=default"

    def make_requests_from_url(self, url):
        # use local cookies(if available) to login
   
        # cookie_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + \
        #                   "/cookies/" + self.name + ".cookie"
        # cookies = pickle.load(open(cookie_path,"rb"))
        # # cookies is a list of dict
        # cookie_dict = dict()
        # for cookie in cookies:
        #     cookie_dict[cookie['name']] = cookie['value']

        #login with selenium and get cookies(if not available)
            #  open chrome manually
            # 1.make sure that no chrome is running
            # 2. cmd: /usr/bin/google-chrome-stable --remote-debugging-port=9232
        from selenium.webdriver.chrome.options import Options
        chrome_option = Options()
        chrome_option.add_argument("--disable-extensions")
        chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        # connect to the browser opened
        browser = webdriver.Chrome(executable_path=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) +
                                "/chromedriver/chromedriver",chrome_options= chrome_option)
        sign_in_url = url
        browser.get(sign_in_url)

        # username and password input
        from selenium.webdriver.common.keys import Keys

        browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper > input"). \
                send_keys(Keys.CONTROL+"a")

        browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper > input").\
                send_keys("your username")

        browser.find_element_by_css_selector("div.SignFlow-password > div > div.Input-wrapper > input").\
                send_keys(Keys.CONTROL+"a")

        browser.find_element_by_css_selector("div.SignFlow-password > div > div.Input-wrapper > input"). \
                send_keys("your password")

            # click the login button - two ways
                # 1.find css element，click

        browser.find_element_by_css_selector("#root > div > main > div > div > div > div.SignContainer-inner > "
                                                 "div.Login-content > form > button").click()

                #2. control mouse, click
            # import pyautogui
            # pyautogui.moveTo(895,603)
            # pyautogui.click()

            # get cookies
        time.sleep(10) #!!!! some time to allow cookie-getting
        cookies = browser.get_cookies()
        cookie_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + \
                          "/cookies/" + self.name + ".cookie"
        pickle.dump(cookies, open(cookie_path,'wb'))
            # cookies is a list of dict

        cookie_dict  = dict()
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        return scrapy.Request(url=url, dont_filter=True, cookies=cookie_dict, headers=self.headers)


    def parse(self, response):
        
        # filter url that's not in format: /question/xxx  e.g. /question/264921970/answer/732102527

        all_urls = response.css("a::attr(href)").extract()
        http_urls = [parse.urljoin(response.url, url) for url in all_urls]

        for url in http_urls:
            if re.match(".*/question/(\d)+(/|$).*",url):
                try:
                    question_id = int(re.search(".*/question/((\d)+)(/|$).*",url).group(1))
                    que_url = re.search("(.*)/answer/.*",url).group(1)
                except:
                    continue

                yield scrapy.Request(url = que_url, headers=self.headers,
                                     meta = {"zhihu_id":question_id,
                                             "url":que_url },
                                     callback=self.parse_question)
            else:
                # yield scrapy.Request(url = url, headers=self.headers, callback= self.parse)
                continue

        # yield scrapy.Request(self.zhihu_start_url.format(3,6),headers=self.headers, callback= self.parse_portal)


    def parse_question(self,response):

        time.sleep(0.5)

        item_loader = ItemLoader(item = ZhihuQuestionItem(), response = response)

        item_loader.add_value("zhihu_id",response.meta.get("zhihu_id"))
        item_loader.add_value("url", response.meta.get("url"))
        item_loader.add_css("topics", ".QuestionHeader-topics > div > span > a > div > div::text")
        item_loader.add_css("title", ".QuestionHeader-title::text")
        item_loader.add_css("content", ".QuestionRichText.QuestionRichText--expandable > div > span")
        item_loader.add_css("answer_num", ".List-headerText > span::text")
        item_loader.add_css("comments_num", ".QuestionHeader-Comment > button::text")
        item_loader.add_css("watch_user_num",".NumberBoard.QuestionFollowStatus-counts.NumberBoard--divider"
                                              " > button > div > strong::text")
        item_loader.add_css("click_num", ".NumberBoard.QuestionFollowStatus-counts.NumberBoard--divider > "
                                         "div > div > strong::text")

        item_loader.add_value("crawl_time", datetime.datetime.now())

        que_item = item_loader.load_item()

        time.sleep(1.5)
        yield scrapy.Request(self.answer_start_url.format(response.meta.get("zhihu_id"), 5, 0),
                             headers=self.headers, callback= self.parse_answer)

        yield que_item



    def parse_answer(self,response):
        time.sleep(0.5)
        answers_json = json.loads(response.text)
        answer_data_list = answers_json["data"]

        for answer_data in answer_data_list:

            item_loader = ItemLoader(item=ZhihuAnswerItem(), response=response)

            item_loader.add_value("zhihu_id",answer_data["id"])
            item_loader.add_value("url",answer_data["url"])
            item_loader.add_value("question", answer_data["question"]["title"])
            item_loader.add_value("question_id",answer_data["question"]["id"])
            item_loader.add_value("author_id",answer_data["author"]["name"])
            item_loader.add_value("content",answer_data["content"])
            item_loader.add_value("praise_num",answer_data["voteup_count"])
            item_loader.add_value("comments_num",answer_data["comment_count"])
            item_loader.add_value("create_time",answer_data["created_time"])
            item_loader.add_value("update_time",answer_data["updated_time"])
            item_loader.add_value("crawl_time",datetime.datetime.now())

            answer_item = item_loader.load_item()
            yield answer_item
            time.sleep(1.5)

        if answers_json["paging"]["is_end"] == False:
            next_ans_url = answers_json["paging"]["next"]
            scrapy.Request(url = next_ans_url, headers=self.headers, callback= self.parse_answer)


    def parse_portal(self,response):
        time.sleep(0.5)
        portal_json = json.loads(response.text)

        data = portal_json["data"]  # data is a list of 6 elements, each a data json
        for record in data:
            que_id  = record["target"]["question"]["id"]
            que_url = self.start_urls[0] + "/question/" + que_id
            yield scrapy.Request(url = que_id, headers=self.headers, callback= self.parse_question)
            time.sleep(0.5)
            yield scrapy.Request(url=que_id, headers=self.headers, callback=self.parse)

        if portal_json["paging"]["is_end"] == False:
            next_portal = portal_json["paging"]["next"]
            yield scrapy.Request(url = next_portal, headers=self.headers, callback=self.parse_portal)
