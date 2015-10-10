from time import sleep
import urllib
__author__ = 'Kasama'

urlString1 = "http://www.imdb.com/search/title?genres=animation&sort=moviemeter,asc&start="
urlString2 = "&title_type=feature"
f = open('test.html', 'w+')


for i in range(1, 500, 50):
    print i
    sleep(60)
    urlString = urlString1.__add__(str(i)).__add__(urlString2)
    htmlPage = urllib.urlopen(urlString)
    f.write(htmlPage.read())

f.close()