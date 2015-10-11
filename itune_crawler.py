__author__ = 'Kasama'

import scrapy
import os
import string
from bs4 import BeautifulSoup

from scrapy.selector import Selector
from string import ascii_uppercase

# from scrapy.http import HtmlResponse
from time import sleep

DOMAIN = 'https://itunes.apple.com/us/genre/'
GENRES = (
         'books-baseball/id10121?mt=11',
         'books-basketball/id10122?mt=11',
         'books-football/id10125?mt=11',
         'books-golf/id10126?mt=11',
         'books-mountaineering/id10128?mt=11',
         'books-outdoors/id10129?mt=11',
         'books-soccer/id10132?mt=11',
         'books-training/id10133?mt=11',
         'books-water-sports/id10134?mt=11',
         'books-winter-sports/id10135?mt=11',
        )
# basketball - https://itunes.apple.com/us/genre/books-basketball/id10122?mt=11
# baseball - https://itunes.apple.com/us/genre/books-baseball/id10121?mt=11
# football - https://itunes.apple.com/us/genre/books-football/id10125?mt=11
# golf - https://itunes.apple.com/us/genre/books-golf/id10126?mt=11
# mountaineering - https://itunes.apple.com/us/genre/books-mountaineering/id10128?mt=11
# outdoor - https://itunes.apple.com/us/genre/books-outdoors/id10129?mt=11
# soccer - https://itunes.apple.com/us/genre/books-soccer/id10132?mt=11
# training - https://itunes.apple.com/us/genre/books-training/id10133?mt=11
# water sports - https://itunes.apple.com/us/genre/books-water-sports/id10134?mt=11
# winter sports - https://itunes.apple.com/us/genre/books-winter-sports/id10135?mt=11

class ItuneSpider(scrapy.Spider):
    letter_dir = ''
    name = 'itune'
    start_urls = ['https://itunes.apple.com/us/genre/books-basketball/id10122?mt=11&letter=A']

    def parse(self, response):
        for genre in GENRES:
            genre_url = DOMAIN + genre
            genre_dir = genre[:genre.find('/')]
            self.make_dir(genre_dir)
            for letter in ascii_uppercase+'*':
                letter_url = genre_url + '&letter=' + letter
                if letter == '*':
                    letter = '0'
                self.letter_dir = genre_dir+"/"+letter
                self.make_dir(self.letter_dir)
                request = scrapy.Request(letter_url, callback=self.parse_page)
                request.meta['letterDir'] = self.letter_dir
                yield request

    def parse_page(self, response):
        for href in response.css('.grid3-column ul li a::attr(href)'):
            url = href.extract()
            sleep(2)
            request = scrapy.Request(url, callback=self.parse_item)
            request.meta['letterDir'] = response.meta['letterDir']
            yield request

    def parse_item(self, response):
        letter_dir = response.meta['letterDir']
        url = response.url
        id_start = url.find('/id')
        id_end = url.find('?')
        id = url[id_start+3:id_end]
        self.dump_file(url,response.body,letter_dir)
        sel = Selector(response)
        rating_stars = len(sel.xpath('//div[@id="left-stack"]//span[@class="rating-star"]'))*1.0 + len(sel.xpath('//div[@id="left-stack"]//span[@class="rating-star half"]'))*0.5
        description = BeautifulSoup(sel.xpath('//div[@itemprop="description"]//p').extract_first()).text
        yield {
            'id': id,
            'url': sel.xpath('//head/link[@rel="canonical"]/@href').extract()[0],
            'title': sel.xpath('//div[@id="title"]/div/h1[1]/text()').extract_first(),
            'author': sel.xpath('//div[@id="title"]/div/h2/span/text()').extract_first(),
            'short_description': sel.xpath('//div[@id="title"]/div/h3/span/text()').extract_first(),
            'description': description,
            'price': sel.xpath('//div[@class="price"]/text()').extract_first(),
            'genre': sel.xpath('//li[@class="genre"]/a/span[@itemprop="genre"]/text()').extract_first(),
            'date': sel.xpath('//li/span[@itemprop="dateCreated"]/text()').extract_first(),
            'publisher': sel.xpath('//li/span[@itemprop="publisher"]/span[@itemprop="name"]/text()').extract_first(),
            'language': sel.xpath('//li[@class="language"]/text()').extract_first(),
            'seller': sel.xpath('//div[@class="lockup product ebook"]/ul[@class="list"]/li[6]/text()').extract_first(),
            'length': sel.xpath('//div[@class="lockup product ebook"]/ul[@class="list"]/li[7]/text()').extract_first(),
            'rating_value': sel.xpath('//div[@class="rating"]/span[@itemprop="ratingValue"]/text()').extract_first(),
            'rating_star': rating_stars,
        }

    def dump_file(self,url,body,path):
        i = url.find('?')
        url = url[len('https://itunes.apple.com/us/book/'):i].replace('/', '_').replace('&', '_').replace('=', '_')
        file_name = path+'/'+url + '.html'
        with open(file_name, 'w') as dump:
            dump.write(body)

    def make_dir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)