# -*- coding: utf-8 -*-
import scrapy
import re
import json
from ..items import EstateItem
from scrapy.linkextractors import LinkExtractor


class HousesSpider(scrapy.Spider):
    name = 'houses'
    # allowed_domains = ['cs.lianjia.com', 'bj.lianjia.com']
    start_urls = ['https://cs.lianjia.com/']
    street_set = set()
    estate_set = set()

    def parse(self, response):
        pattern = '^https://[a-z][a-z].lianjia.com/$'
        le = LinkExtractor(allow=pattern)
        links = le.extract_links((response))
        for link in links:
            city_href = link.url + 'xiaoqu/'
            yield scrapy.http.Request(city_href, callback=self.parse_city)

    def parse_city(self, response):
        city_href = response.url
        if 'xiaoqu' in city_href:
            districts_list = response.xpath('//div[@data-role="ershoufang"]/div/a[not(@target)]')
            for district in districts_list:
                district_string = district.xpath('./@href').extract()
                if district_string:
                    search = re.search(r'(/xiaoqu/)(.*)', district_string[0])
                    if search:
                        district_href = city_href + search.group(2)
                        yield scrapy.http.Request(district_href, callback=self.parse_district)
        else:
            with open('wrong-city.txt', 'a+') as fr:
                fr.write(city_href+'\n')

    def parse_district(self, response):
        district_href = response.url
        city_href = re.search(r'(.*)(/xiaoqu.*)', district_href).group(1)
        street_list = response.xpath('//div[@data-role="ershoufang"]/div[last()]/a')
        for street in street_list:
            street_name = street.xpath('./text()').extract_first()
            if street_name not in self.street_set:
                if street_name:
                    street_string = street.xpath('./@href').extract_first()
                    if street_string:
                        street_href = city_href + street_string
                        yield scrapy.http.Request(street_href, callback=self.parse_street)
                    self.street_set.add(street_name)

    def parse_street(self, response):
        street_href = response.url
        totalpage_string = response.xpath('//div[@page-data]/@page-data').extract_first()
        if totalpage_string:
            page_num = json.loads(totalpage_string)['totalPage']
            for i in range(page_num):
                cur_page = 'pg' + str(i + 1) + '/'
                street_page = street_href + cur_page
                yield scrapy.http.Request(street_page, callback=self.parse_street_page)

    def parse_street_page(self, response):
        estate_list = response.xpath('//ul[@class="listContent"]/li')
        for estate in estate_list:
            ename = estate.xpath('.//div[@class="title"]/a/text()').extract_first()
            if ename not in self.estate_set:
                estate_href = estate.xpath('./a[@class="img"]/@href').extract_first()
                yield scrapy.http.Request(estate_href, callback=self.parse_estate)
                self.estate_set.add(ename)

    def parse_estate(self, response):
        position = re.search(r"(resblockPosition:')(.*)(',)", response.text)
        city_name = re.search(r"(city_name: ')(.*)(',)", response.text)
        if position and city_name:
            position = position.group(2)
            city_name = city_name.group(2)
            long = float(position.split(',')[0])
            lat = float(position.split(',')[1])
            estate_item = EstateItem()
            estate_item['avg_price'] = response.xpath('//span[@class="xiaoquUnitPrice"]/text()').extract_first()
            estate_item['estate_name'] = response.xpath('//h1[@class="detailTitle"]/text()').extract_first()
            estate_item['long'] = long
            estate_item['lat'] = lat
            estate_item['city_name'] = city_name
            yield estate_item
