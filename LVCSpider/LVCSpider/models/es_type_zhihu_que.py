# -*- coding: utf-8 -*-

from elasticsearch_dsl import Document, Date, Integer, Keyword, Text
from elasticsearch_dsl.connections import connections
from LVCSpider.settings import ES_HOST


connections.create_connection(hosts=[ES_HOST])


class ZhihuQueType(Document):

    zhihu_id = Integer()
    topics = Text(analyzer="ik_max_word")
    url = Keyword()
    title = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    answer_num = Integer()
    comments_num = Integer()
    watch_user_num = Integer()
    click_num = Integer()
    crawl_time = Date()

    class Index:
        name = "zhihu_question"



if __name__ == "__main__":
    ZhihuQueType.init()
