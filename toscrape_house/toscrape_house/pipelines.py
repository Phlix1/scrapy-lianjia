# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem


class ToscrapeHousePipeline(object):
    def process_item(self, item, spider):
        return item


class DuplicatesPipeline(object):
    def __init__(self):
        self.estate_set = set()

    def process_item(self, item, spider):
        name = item['estate_name']
        if name in self.estate_set:
            raise DropItem("Duplicate estate found: %s" % item)
        self.estate_set.add(name)
        return item


class DeletenonePipeline(object):
    def process_item(self, item, spider):
        price = item['avg_price']
        if price is None:
            raise DropItem("invalid estate found: %s" % item)
        return item


class DatacleanPipeline(object):
    def process_item(self, item, spider):
        estate_name = item['estate_name']
        if ',' in estate_name:
            item['estate_name'] = estate_name.replace(',', ' ')
        return item
