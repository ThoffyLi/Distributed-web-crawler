# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from LVCSpider.models.es_type_zhihu_que import ZhihuQueType


class ElasticSearchPipeline(object):

    def process_item(self, item, spider):

        item.save_to_es()
        return item
