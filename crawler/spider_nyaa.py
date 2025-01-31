
from modules.spiders import PageParser,MultiLevelSpider
from urllib.parse import urljoin

ROOT_URL = "https://sukebei.nyaa.si/"


class TitleParser(PageParser):
    async def parse(self, soup, url):
        links = soup.select('table.torrent-list tr td[colspan="2"] a:not([class])')
        return {'titles':[link['title'] for link in links]}

    def get_next_links(self, soup, url):
        links = soup.select('table.torrent-list tr td[colspan="2"] a')
        return [urljoin(url,link['href']) for link in links]

    def get_next_depth(self, current_depth):
        return current_depth + 1

    def get_pagination_params(self):
        return [{'p': f'{i}'} for i in range(1, 3)]  #TODO:测试 2页


class InfoParser(PageParser):
    async def parse(self, soup, url):
        links = soup.select('div.panel-body')
        return {'titles':[link['title'] for link in links]}

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
            's':'id',   # Sort 默认 date(id)
            'o':'desc',  # order 降序(desc),升序(asc)
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

    def setSort(self,sort:str):
        if sort:
            self.params['s'] = sort

    def setOrder(self,order:str):
        if order:
            self.params['o'] = order

    def crawl(self):

        parsers = {
            0: TitleParser(),
        }

        spider = MultiLevelSpider(ROOT_URL, parsers, max_depth=1)
        results = spider.start(ROOT_URL,self.params)

        # print(results)
        spider.save_to_csv("results.csv")
        # for title in results[0]:
        #     print(title)
