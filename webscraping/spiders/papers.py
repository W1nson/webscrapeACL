import scrapy
import os 
import re
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time 

from bs4 import BeautifulSoup

from webscraping.spiders.db import dbConnect


main = 'https://openreview.net/group?id=aclweb.org/ACL/ARR'
paper = 'https://openreview.net/forum?id='


class PaperSpider(scrapy.Spider):
    name = "papers"

    def __init__(self): 
        opts = webdriver.ChromeOptions()
        opts.headless = True
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        self.db = dbConnect()
        # self.db.create()
       
    def start_requests(self):
        yield scrapy.Request(url=main, callback=self.parse)

    def parse(self, response):
        js = response.css('script::text').getall()
        years = re.findall(r'\"url\": \"(.+?)\"', js[1].replace("\\",""))
        years = [year.split('/')[-1] for year in years]
        
        for year in years: 
            yield scrapy.Request(url=main+'/'+year, callback=self.parseMonth,meta={'year': year})

    def parseMonth(self, response): 
        year = response.meta.get('year')
        js = response.css('script::text').getall()
        months = re.findall(r"\"url\": \"(.+?)\"", js[1].replace("\\",""))
        months = [month.split('/')[-1] for month in months]

        for month in months: 
            if month =='Jun': 
                if self.db.checkExists(year, 'June'): 
                    print(year, month, "Exists")
                    continue 
            else: 
                if self.db.checkExists(year, month): 
                    print(year, month, "Exists")
                    continue 
            
            yield scrapy.Request(url=main+'/'+year+'/'+month, callback=self.parseID, meta={'year':year, 'month':month})

    def parseID(self, response): 
        year = response.meta.get('year')
        month = response.meta.get('month')
        if month == 'Jun':
            month = 'June'
        js = response.css('script::text').getall()
        ids = re.findall(r"href=\"(.+?)\"", js[1].replace("\\",""))
        ids = [id for id in ids if 'forum?' in id]

        if len(ids) == 0: 
            self.driver.get(response.url)
            time.sleep(3)
            html_source = self.driver.page_source 
            
            soup = BeautifulSoup(html_source,'lxml')

            find = soup.find_all("li", {"class": "note"})
            count = len(find)
            print(year, month,count)
            for titles in find:
                data = dict()

                id = titles.get('data-id')
                if id is None: 
                    continue 
                
                yield scrapy.Request(url=paper+id, callback=self.parseInfo, meta={'id': id, 'year':year, 'month':month}) 
            
        else: 
            for id in ids: 
                if 'forum' in id: 
                    id = id.split('=')[-1]
                    yield scrapy.Request(url=paper+id, callback=self.parseInfo, meta={'id': id, 'year':year, 'month':month}) 
        
            
           
    
    def parseInfo(self, response): 
        id = response.meta.get('id')
        year = response.meta.get('year')
        month = response.meta.get('month') 
        
        data = dict()
        data['id'] = id 
        data['forum'] = paper + id 
        data['pdf'] = 'https://openreview.net/pdf?id=' + id
        data['title'] = response.xpath("//div[@class='title_pdf_row']/h2/text()").get()
        additional = response.xpath("//strong[@class='note-content-field']/text()").getall()
        additional = [ a for a in additional if a != ':']
        items = response.xpath("//span[@class='note-content-value']/text()").getall()
        links = response.xpath("//span[@class='note-content-value']/a/@href").getall()
        items = items+links
        for a, b in zip(additional, items): 
            if a == 'Abstract':
                data[a] = b

        data['year'] = year
        data['month'] = month
        self.db.insert(data)
        yield data 
        # self.db.insert(data)