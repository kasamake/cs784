import scrapy
import os
import re
import string
from bs4 import BeautifulSoup

from scrapy.selector import Selector
from string import ascii_uppercase

# from scrapy.http import HtmlResponse
from time import sleep

DOMAIN = 'http://www.ebooks.com/subjects/'
GENRES = (
         'sports-recreation-baseball-ebooks/379/?page=',
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

class EbookSpider(scrapy.Spider):
    genre_dir = ''
    name = 'ebook'
    start_urls = ['http://www.ebooks.com/subjects/sports-recreation-baseball-ebooks/379/?page=1']
    empty_page = {}

    def parse(self, response):
        for genre in GENRES:
            genre_url = DOMAIN + genre
            genre_dir = genre[:genre.find('/')]
            self.make_dir(genre_dir)

            page_no = 1
            self.empty_page[genre_url] = False
            while page_no < 2 and not self.empty_page[genre_url]:
                letter_url = genre_url + str(page_no)
                page_no += 1

                request = scrapy.Request(letter_url, callback=self.parse_page)
                request.meta['pageKey'] = genre_url
                request.meta['genreDir'] = genre_dir
                yield request

            # for letter in ascii_uppercase+'*':
            #     letter_url = genre_url + '&letter=' + letter
            #     if letter == '*':
            #         letter = '0'
            #     self.letter_dir = genre_dir+"/"+letter
            #     self.make_dir(self.letter_dir)
            #
            #
            #     request = scrapy.Request(letter_url, callback=self.parse_page)
            #     request.meta['pageKey'] = genre_url
            #     yield request

    def parse_page(self, response):
        #Check the page
        bookLinks = response.css('.book-title a::attr(href)')
        if len(bookLinks) == 0:
            self.empty_page[response.meta['pageKey']] = True
            return

        hrefs = bookLinks.extract()
        for url in hrefs:
            #print "\n####"
            #print url
            #print "\n####"
            sleep(2)
            request = scrapy.Request(url, callback=self.parse_item)
            request.meta['genreDir'] = response.meta['genreDir']
            yield request

    def parse_item(self, response):
        genre_dir = response.meta['genreDir']
        url = response.url
        url_split = url.split('/')
        id = url_split[3]
        # print('----ID----')
        # print(id)
        # self.dump_file(url,response.body, genre_dir)
        sel = Selector(response)
        soup = BeautifulSoup(response.body)
        try:
            description = soup.find("div", { "class" : "short-description" }).text
            price = soup.find("span", { "itemprop" : "price" }).text
            publishBlock = soup.find("div", {"class":"publish"}).text
            target = re.split(";", publishBlock)[1].split(' ')[:3]
            month = target[1]
            year = target[2][:4]
            pages = target[2][4:]
            # >>> target = re.split(";", st)[1].split(' ')[:3]
            # >>> target
            # [u'', u'October', u'2015ISBN']
            # >>> target[1]
            # u'October'
            # >>> target[2][:4]
            # u'2015'
            # >>> target[2][4:]
            # u'ISBN'
        except AttributeError:
            description = ""
            price = ""
            print "\nError with parsing response: {0}\n".format(response.url)
        # rating_stars = len(sel.xpath('//div[@class="rating-icons"]/div[@class="rating-star-icon"]'))*1.0 + len(sel.xpath('//div[@id="left-stack"]//span[@class="rating-star half"]'))*0.5
        yield {
            'id': id,
            # 'url': sel.xpath('//head/link[@rel="canonical"]/@href').extract()[0],
            'title': sel.xpath('//div[@class="book-info-head"]/h1[1]/text()').extract_first(),
            'author': sel.xpath('//div[@class="book-info-head"]/div[@class="authors"]/a[1]/text()').extract_first(),
            'short_description': sel.xpath('//div[@class="book-info-head"]/h2[1]/text()').extract_first(),
            'description': description.strip().strip('more').strip(),
            'price': price.strip(),
            # 'genre': sel.xpath('//li[@class="genre"]/a/span[@itemprop="genre"]/text()').extract_first(),
            'date': month + " " + year,
            'publisher': sel.xpath('//div[@class="publish-box"]/div[@class="publish"]/a[1]/text()').extract_first(),
            # 'language': sel.xpath('//li[@class="language"]/text()').extract_first(),
            # 'seller': sel.xpath('//div[@class="lockup product ebook"]/ul[@class="list"]/li[6]/text()').extract_first(),
            'length': pages.strip('ISBN'),
            # 'rating_value': sel.xpath('//div[@class="rating"]/span[@itemprop="ratingValue"]/text()').extract_first(),
            # 'rating_star': rating_stars,
        }

    def dump_file(self,url,body,path):
        i = url.find('?')
        url = url[len('http://www.ebooks.com/'):i].replace('/', '_').replace('&', '_').replace('=', '_')
        file_name = path+'/'+url + '.html'
        with open(file_name, 'w') as dump:
            dump.write(body)

    def make_dir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
