# -*- coding: utf-8 -*-

# Define here the models for your scraped items

import scrapy
import datetime
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from LVCSpider.models.es_type_zhihu_que import ZhihuQueType
from LVCSpider.models.es_type_zhihu_ans import ZhihuAnsType
from LVCSpider.models.es_type_lagou import LagouType
from LVCSpider.models.es_type_hupu import HupuType
from elasticsearch_dsl.connections import connections
from LVCSpider.settings import ES_HOST

class TakeFirstLoader(ItemLoader):
    default_output_processor = TakeFirst()

es_hupu = connections.create_connection(hosts = [ES_HOST])

def generate_suggests(es, info_tuple):
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            words = es.indices.analyze(index="hupu",
                                       body={"analyzer": "ik_max_word", "text": "{0}".format(text)})
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})

    return suggests

# Hupu ---------------------------------------------------------------------------------------
def author_level_trans(value):
    value = int(re.search('([-]?\d+)',value).group(1))
    return value

def Liangs_trans(value):
    value = int(re.search('([-]?\d+).+', value).group(1))
    return value

def get_reply(value):
    value = int(re.search('(\d+)[\D]*[/][\D]*\d+',value).group(1))
    return value

def get_views(value):
    value = int(re.search('\d+[\D]*[/][\D]*(\d+)',value).group(1))
    return value

def time_trans(value):
    value = datetime.datetime.strptime(value,"%Y-%m-%d %H:%M")
    return value

def date_trans(value):
    value = datetime.datetime.strptime(value,"%Y-%m-%d").date()
    return value

class HpspiderItem(scrapy.Item):

    url = scrapy.Field()
    title =  scrapy.Field()
    author_id = scrapy.Field()

    author_level =  scrapy.Field(
        input_processor = MapCompose(author_level_trans)
    )

    Liangs = scrapy.Field(
        input_processor = MapCompose(Liangs_trans)
    )


    reply_num = scrapy.Field(
        input_processor = MapCompose(get_reply)
    )

    views = scrapy.Field(
        input_processor=MapCompose(get_views)
    )


    create_time = scrapy.Field(
        input_processor=MapCompose(time_trans)
    )

    create_date =  scrapy.Field(
        input_processor=MapCompose(date_trans)
    )

    page = scrapy.Field(
    )


    def save_to_es(self):

        hupu = HupuType()

        hupu.title = self["title"]
        hupu.url = self["url"]
        hupu.author_id = self["author_id"]
        hupu.author_level = self["author_level"]
        hupu.Liangs = self["Liangs"]
        hupu.reply_num = self["reply_num"]
        hupu.views = self["views"]
        hupu.create_time = self["create_time"]
        hupu.create_date = self["create_date"]
        hupu.page = self["page"]

        # suggest
        hupu.suggest = generate_suggests(es_hupu,((hupu.title,10),))

        hupu.save()

# -------------------------------------------------------------------------------------------------

#Zhihu Question
def content_handle(content):
    if content is None:
        return "N/A"
    else:
        result = re.search("<.*>(.*)<.*>",content).group(1)
        if result == "":
            result = "N/A"
        return result

def answer_num_extract(value):
    try:
        result = int(value.replace(",",""))
    except:
        result = 0
    return result

def comments_num_extract(value):
    try:
        result = int(value.split("条")[0])
    except:
        result = 0
    return result

def comma_elim(value):
    return int(value.replace(",",""))



class ZhihuQuestionItem(scrapy.Item):

    zhihu_id = scrapy.Field(
        output_processor = TakeFirst()
    )

    topics = scrapy.Field(

        output_processor = Join(" | ")
    )

    url = scrapy.Field(
        output_processor=TakeFirst()
    )

    title = scrapy.Field(
        output_processor=TakeFirst()
    )

    content = scrapy.Field(
        input_processor = MapCompose(content_handle),
        output_processor=TakeFirst()
    )

    answer_num = scrapy.Field(
        input_processor = MapCompose(answer_num_extract),
        output_processor=TakeFirst()
    )

    comments_num = scrapy.Field(
        input_processor=MapCompose(comments_num_extract),
        output_processor=TakeFirst()
    )

    watch_user_num = scrapy.Field(
        input_processor=MapCompose(comma_elim),
        output_processor=TakeFirst()
    )

    click_num = scrapy.Field(
        input_processor=MapCompose(comma_elim),
        output_processor=TakeFirst()
    )

    crawl_time = scrapy.Field(
        input_processor = MapCompose(lambda x:datetime.datetime.strptime(str(x).split(".")[0],"%Y-%m-%d %H:%M:%S")),
        output_processor=TakeFirst()
    )


    def save_to_es(self):

        zhihu_que = ZhihuQueType()

        zhihu_que.zhihu_id = self["zhihu_id"]
        zhihu_que.url = self["url"]
        zhihu_que.content = self["content"]
        zhihu_que.answer_num = self["answer_num"]
        zhihu_que.click_num = self["click_num"]
        zhihu_que.comments_num = self["comments_num"]
        zhihu_que.crawl_time = self["crawl_time"]
        zhihu_que.watch_user_num = self["watch_user_num"]
        zhihu_que.topics = self["topics"]
        zhihu_que.title = self["title"]

        zhihu_que.save()



#Zhihu Answer----------------------------------------------

def author_id(value):
    if value is None or value == "":
        result = "N/A"
    else:
        result = value
    return result

def content_handle(content):
    return re.sub("<.*?>","",content)


def timestamp_trans(timestamp):
    time_str = str(datetime.datetime.fromtimestamp(timestamp))
    return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

class ZhihuAnswerItem(scrapy.Item):

    zhihu_id = scrapy.Field(
        output_processor=TakeFirst()
    )

    url = scrapy.Field(
        output_processor=TakeFirst()
    )

    question_id = scrapy.Field(
        output_processor=TakeFirst()
    )

    question = scrapy.Field(
        output_processor=TakeFirst()
    )

    author_id = scrapy.Field(
        input_processor = MapCompose(author_id),
        output_processor=TakeFirst()
    )

    content = scrapy.Field(
        input_processor = MapCompose(content_handle),
        output_processor=TakeFirst()
    )

    praise_num = scrapy.Field(
        output_processor=TakeFirst()
    )
    comments_num = scrapy.Field(
        output_processor=TakeFirst()
    )
    create_time = scrapy.Field(
        input_processor = MapCompose(timestamp_trans),
        output_processor=TakeFirst()
    )

    update_time = scrapy.Field(
        input_processor = MapCompose(timestamp_trans),
        output_processor=TakeFirst()
    )

    crawl_time = scrapy.Field(
        input_processor = MapCompose(lambda x: datetime.datetime.strptime(str(x).split(".")[0], "%Y-%m-%d %H:%M:%S")),
        output_processor = TakeFirst()
    )


    def save_to_es(self):

        zhihu_ans = ZhihuAnsType()

        zhihu_ans.zhihu_id = self["zhihu_id"]
        zhihu_ans.url =  self["url"]
        zhihu_ans.question = self["question"]
        zhihu_ans.question_id = self["question_id"]
        zhihu_ans.author_id = self["author_id"]
        zhihu_ans. content = self["content"]
        zhihu_ans.praise_num = self["praise_num"]
        zhihu_ans.comments_num = self["comments_num"]
        zhihu_ans.create_time = self["create_time"]
        zhihu_ans.update_time = self["update_time"]
        zhihu_ans.crawl_time = self["crawl_time"]

        zhihu_ans.save()



# Lagou -------------------------------------------------------------------------------------------------------------------------

def id_extract(url):
    try:
        id = int(re.search(".*jobs/(\d+)[.]html.*",url).group(1))
    except:
        id = 0
    return id


def salary_calc(value):
    lower = int(re.search("(\d+).*?(\d+).*",value).group(1))
    upper = int(re.search("(\d+).*?(\d+).*",value).group(2))
    return int(1000*(lower + upper)/2)

def loc_trans(value):
    return re.search("/(.*)/",value).group(1).strip()

def company_trans(value):
    return value.strip()

def edu_trans(value):
    return re.search("(.*)/",value).group(1).strip()

def content_clean(value):
    try:
        content = value.strip().replace("\n", "")
    except:
        content ="N/A"

    return content


class LagouspiderItem(scrapy.Item):


    content = scrapy.Field(
        name_in = MapCompose(content_clean),
        input_processor = Join()
    )

    url = scrapy.Field()
    job_title = scrapy.Field()

    company = scrapy.Field(
        input_processor = MapCompose(company_trans)
    )

    salary = scrapy.Field(
        input_processor = MapCompose(salary_calc)
    )

    location = scrapy.Field(
        input_processor = MapCompose(loc_trans)
    )

    education_req = scrapy.Field(
        input_processor=MapCompose(edu_trans)
    )

    def save_to_es(self):

        lagou = LagouType()

        lagou.job_title = self["job_title"]
        lagou.url = self["url"]
        lagou.company = self["company"]
        lagou.education_req = self["education_req"]
        lagou.location = self["location"]
        lagou.content = self["content"]
        lagou.salary = self["salary"]

        lagou.save()

