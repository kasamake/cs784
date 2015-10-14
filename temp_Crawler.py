# -*- coding: utf-8 -*-


import errno
import os
import scrapy

from scrapy.selector import Selector
from bs4 import BeautifulSoup
from scrapy.contrib.loader import XPathItemLoader
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider


DOMAIN = 'www.ebooks.com/subjects/sports-recreation/?sortBy=&sortOrder=&RestrictBy=&countryCode=us&page='
SITE_DOMAIN = 'https://' + DOMAIN
dir = 'ebooksTable'

class ebooks(BaseSpider):
    name = 'ebooks'
    allowed_domains = [DOMAIN]

    def __init__(self, *args, **kwargs):
        self.seen = set()
        
	self.make_dir(dir)
       

    def start_requests(self):
	l = []
	l.extend(range(1,1414))
	l.append('*')
	
	for i in l:
	    page_url = SITE_DOMAIN + str(i)
	    yield scrapy.Request(page_url, callback=self.parse_page)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        for url in hxs.select('//span[@id= "lblResults"]/h4/a/@href').extract():
            book_id = self.getID(url)
            if book_id not in self.seen:
                self.seen.add(book_id)
                yield Request(url, callback=self.parse_item)

    def parse_item(self, response):
        self.dump(response.url, response.body)
        url = response.url
        id = getID(url)
        sel = Selector(response)

	yield {
            'id': id,
            'url': url,
            'author': sel.xpath('//div[@class="book-details floatRight”]/div[@class=“authors”]/a/text()').extract_first(),
            'short_description': sel.xpath('//div[@class="book-details floatRight"]/h2/text()').extract_first(),
	    'description': sel.xpath('//div[@class="book-info-body book-description”]/span[@itemprop=“description”]/text()').extract_first(),
            'price': sel.xpath('//li[@class="clearfix"]/text()').extract_first(),
            #’genre': sel.xpath('//li[@class="genre"]/a/span[@itemprop="genre"]/text()').extract_first(),
            'date': sel.xpath('//div[@ class ="publish"]/text()').extract_first(),   # you wen ti!!!!!!!!!!
            'publisher': sel.xpath('//div[@ class ="publish"]/text()').extract_first(),
            #’language': sel.xpath('//li[@class="language"]/text()').extract_first(),
            'seller': sel.xpath('//div[@class ="publish"]/text()').extract_first(),
            'length': sel.xpath('//div[@class ="publish"]/text()').extract_first(),
            'rating_value': sel.xpath('//div[@id="pd_rating_holder_7947770"]/span[@itemprop="ratingValue"]/text()').extract_first(),
            #’rating_star': rating_stars,
	    'isbn': sel.xpath('//div[@class ="isbn-info"]/text()').extract_first(),


        }

  


    def dump(self, url, body):
        filename = '{0}/{1}'.format(dir, self.dump_filename(url))
        with open(filename, 'w') as dump:
            dump.write(body)

    def dump_filename(self, url):
        id = self.getID(url)
        return id + '.html'
   
    def getID(url):
        m = re.match('.*com/(\d*)', url )
        return m.group(1)


    def make_dir(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise
