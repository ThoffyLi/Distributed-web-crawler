# -*- coding: utf-8 -*-

from elasticsearch_dsl import Document, Date, Integer, Keyword, Text
from elasticsearch_dsl.connections import connections
from LVCSpider.settings import ES_HOST


connections.create_connection(hosts=[ES_HOST])


class ZhihuAnsType(Document):

    zhihu_id = Integer()
    url = Keyword()
    question = Text(analyzer="ik_max_word")
    question_id = Integer()
    author_id = Keyword()
    content = Text(analyzer="ik_max_word")
    praise_num = Integer()
    comments_num = Integer()
    create_time = Date()
    update_time = Date()
    crawl_time = Date()

    class Index:
        name = "zhihu_answer"



if __name__ == "__main__":
    ZhihuAnsType.init()
