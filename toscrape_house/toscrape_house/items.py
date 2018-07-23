# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ToscrapeHouseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class EstateItem(scrapy.Item):
    estate_name = scrapy.Field()
    avg_price = scrapy.Field()
    long = scrapy.Field()
    lat = scrapy.Field()
    city_name = scrapy.Field()


class HouseItem(scrapy.Item):
    estate = scrapy.Field()
    sell_price = scrapy.Field()
