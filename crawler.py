import urllib


urlString = "http://www.imdb.com/search/title?genres=animation&sort=moviemeter,asc&start=101&title_type=feature"
f = open('test.html', 'w+')
htmlPage = urllib.urlopen(urlString)

f.write(htmlPage.read())
f.close()

