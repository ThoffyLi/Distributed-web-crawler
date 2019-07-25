# -*- coding: utf-8 -*-

from elasticsearch_dsl import Document, Integer, Keyword, Text
from elasticsearch_dsl.connections import connections
from LVCSpider.settings import ES_HOST


connections.create_connection(hosts=[ES_HOST])

class LagouType(Document):


    content = Text(analyzer="ik_max_word")
    url = Keyword()
    job_title = Text(analyzer="ik_max_word")
    company = Keyword()
    salary = Integer()
    location = Keyword()
    education_req = Text(analyzer="ik_max_word")

    class Index:
        name = "lagou"


if __name__ == "__main__":
    LagouType.init()
