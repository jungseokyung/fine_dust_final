# -*- coding: utf-8 -*-
import re
import scrapy
from naver_fc.items import NaverFcItem
from datetime import timedelta, date
from urllib import parse
import time
import random
from time import sleep

start_date = date(2006, 1, 1)
end_date = date(2012, 12, 31)
cnt_per_page = 10
keyword = "금리"

url_format = "https://search.naver.com/search.naver?where=news&query={1}&sm=tab_opt&sort=0&photo=0&field=0&reporter_article=&pd=3&ds={0}&de={0}&docid=&nso=so%3Ar%2Cp%3Afrom{0}to{0}%2Ca%3Aall&mynews=1&refresh_start=0&related=0&start={2}"

class CoNewsSpider(scrapy.Spider):
    def daterange(start_date, end_date):
        for n in range((int ((end_date - start_date).days)+1)):
            yield start_date + timedelta(n)

    name = 'co_news'
    start_urls = []

    for single_date in daterange(start_date, end_date):
        start_urls.append(url_format.format(single_date.strftime("%Y%m%d"), keyword, 1))

    def parse(self, response):
        for href in response.xpath("//ul[@class='type01']/li/dl/dt/a/@href").extract():
            if 'einfomax' in href:
                yield response.follow(href, self.parse_details)

            if 'news.naver.com' in href:
                yield response.follow(href, self.parse_naver)

        total_cnt = int(re.sub('[()건,]', '', response.xpath("//div[@class='title_desc all_my']/span/text()").get().split('/')[1]))
        query_str = parse.parse_qs(parse.urlsplit(response.url).query)
        currpage = int(query_str['start'][0]) 
        
        startdate = query_str['ds'][0]
        print("=================== [" + startdate + '] ' + str(currpage) + '/' + str(total_cnt) + "===================") 
        if currpage  < total_cnt : 
            yield response.follow(url_format.format(startdate, keyword, currpage+10), self.parse)

    def parse_details(self, response):    
        item = NaverFcItem()
        item['url'] = response.url
        item['title'] = str(response.xpath("//div[@class='article-head-title']/text()").get())
        date = response.xpath("//ul[@class='no-bullet auto-marbtm-0 line-height-6']/li[2]/text()").get()
        item['date'] = date.replace('승인', '').strip()
        content = str(response.xpath("//div[@itemprop='articleBody']/text()").getall())
        content = re.sub(' +', ' ', str(re.sub(re.compile('<.*?>'), ' ', content.replace('\\t','')).replace('\\r','').replace('\t','').replace('\\xa01','').replace('\\xa0','').replace('"','').replace("'",'').replace('\r\n','').replace('\n','').replace('\t','').replace('\u200b','').replace('\\r\\n','').replace('\\n','').strip()))
        item['content'] = content  
        if item['content'] != None:
            yield item

    def parse_naver(self, response):    
        if response.xpath('//*[@id="main_content"]/div[1]/div[1]/a/img/@title').get() == '연합인포맥스':
            item = NaverFcItem()
            item['url'] = response.url
            item['title'] = str(response.xpath("//*[@id='articleTitle']/text()").get())
            item['date'] = response.xpath("//*[@id='main_content']/div[1]/div[3]/div/span/text()").get()
            content = str(response.xpath("//div[@id='articleBodyContents']/text()").getall())

            # if item['title'] == 'None':
            #     item['title'] = str(response.xpath("//div[@class='dable-content-wrapper']/p/text()").get())
            #     item['date'] = response.xpath("//div[@class='section-content']/div/p/span/text()").get()
            #     content = str(response.xpath("//div[@class='dable-content-wrapper']/p/text()").getall())
                
            content = re.sub(' +', ' ', str(re.sub(re.compile('<.*?>'), ' ', content.replace('\\t','')).replace('\\r','').replace('\t','').replace('\\xa01','').replace('\\xa0','').replace('"','').replace("'",'').replace('\r\n','').replace('\n','').replace('\t','').replace('\u200b','').replace(',','').replace('\\r\\n','').replace('\\n','').strip()))
            item['content'] = content  
            if item['content'] != None:
                yield item