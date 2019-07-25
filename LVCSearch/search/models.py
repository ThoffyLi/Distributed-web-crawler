from django.db import models

# Create your models here.

# -*- coding: utf-8 -*-

from elasticsearch_dsl import Document, Integer, Keyword, Text, Date, Completion
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from LVCSearch.settings import ES_HOST


connections.create_connection(hosts = [ES_HOST])

class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return{}

ik_analyzer = CustomAnalyzer("ik_max_word", filter = ["lowercase"])


class HupuType(Document):

    # suggestion
    suggest = Completion(analyzer = ik_analyzer)

    url = Keyword()
    title = Text(analyzer="ik_max_word")
    author_id = Keyword()
    author_level = Integer()
    Liangs = Integer()
    reply_num = Integer()
    views = Integer()
    create_time = Date()
    create_date = Date()
    page = Integer()


    class Index:
        name = "hupu"


if __name__ == "__main__":
    HupuType.init()