
from modules.spiders import PageParser,MultiLevelSpider
from urllib.parse import urljoin

ROOT_URL = "https://sukebei.nyaa.si/"


class MovieSearchParser(PageParser):
    async def parse(self, soup, url):
        titles = soup.select('tr.default td[colspan="2"] a:not([class])')
        return [title['title'] for title in titles]

    def get_next_links(self, soup, url):
        links = soup.select('tr.default td[colspan="2"] a')
        return [urljoin(url,link['href']) for link in links]

    def get_next_depth(self, current_depth):
        return current_depth + 1

class SPnyaa:
    def __init__(self):
        self.params = {
            'f':0,  # filter
            'c':'0_0',  # categories
            'q':'', # query
            'p':1,  # page
        }

    def setWord(self,word:str):
        if word:
            self.params['q'] = word

    def setFilter(self,filter:int):
        if filter:
            self.params['f'] = filter

    def setCategory(self,ca:str):
        if ca:
            self.params['c'] = ca

    def setPage(self,page:int):
        if page:
            self.params['p'] = page

    def crawl(self):

        parsers = {
            0: MovieSearchParser(),
        }

        spider = MultiLevelSpider(ROOT_URL, parsers, max_depth=1)
        results = spider.start(ROOT_URL,self.params)

        for title in results[0]:
            print(title)
