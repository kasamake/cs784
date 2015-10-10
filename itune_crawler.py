__author__ = 'Kasama'

import scrapy
import os
import string
from scrapy.selector import Selector
from string import ascii_uppercase
# from scrapy.http import HtmlResponse
# from time import sleep

DOMAIN = 'https://itunes.apple.com/us/genre/'
GENRES = (
        # 'books-baseball/id10121?mt=11',
        'books-basketball/id10122?mt=11',
        # 'books-boxing/id11054?mt=11',
        )

class ItuneSpider(scrapy.Spider):
    letter_dir = ''
    name = 'itune'
    start_urls = ['https://itunes.apple.com/us/genre/books-basketball/id10122?mt=11&letter=A']

    def parse(self, response):
        for genre in GENRES:
            genre_url = DOMAIN + genre
            genre_dir = genre[:genre.find('/')]
            self.make_dir(genre_dir)
            # for letter in ascii_uppercase+'*':
            for letter in 'A':
                letter_url = genre_url + '&letter=' + letter
                if letter == '*':
                    letter = '0'
                self.letter_dir = genre_dir+"/"+letter
                self.make_dir(self.letter_dir)
                print letter_url
                yield scrapy.Request(letter_url, callback=self.parse_page)
        # for href in response.css('.grid3-column ul li a::attr(href)'):
        #     url = href.extract()
        #     yield scrapy.Request(url, callback=self.parse_page)

        # url = 'https://itunes.apple.com/us/book/the-boys-in-the-boat/id580630645?mt=11'
        # print(url)
        # yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        for href in response.css('.grid3-column ul li a::attr(href)'):
            url = href.extract()
            print(url)
            yield scrapy.Request(url, callback=self.parse_item)

    def parse_item(self, response):
        print(self.letter_dir)
        url = response.url
        id_start = url.find('id')
        id_end = url.find('?')
        id = url[id_start+2:id_end]
        print(id)
        self.dump_file(url,response.body,self.letter_dir)
        sel = Selector(response)
        title = sel.xpath('//div[@id="title"]/div/h1[1]/text()').extract_first()
        print(title)

        rating_stars = len(sel.xpath('//div[@id="left-stack"]//span[@class="rating-star"]'))*1.0 + len(sel.xpath('//div[@id="left-stack"]//span[@class="rating-star half"]'))*0.5
        print 'rating: '
        print rating_stars
        # *1.0 + len(sel.xpath('//div[@id="left-stack"]//span[@class="rating-star half"]'))*0.5)
        yield {
            'id': id,
            'url': sel.xpath('//head/link[@rel="canonical"]/@href').extract()[0],
            'title': sel.xpath('//div[@id="title"]/div/h1[1]/text()').extract_first(),
            'author': sel.xpath('//div[@id="title"]/div/h2/span/text()').extract_first(),
            'short_description': sel.xpath('//div[@id="title"]/div/h3/span/text()').extract_first(),
            'description': sel.xpath('//div[@itemprop="description"]//p').extract_first(),
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
    # scrapy runspider itune_crawler.py -o itune_books.json

    def make_dir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)