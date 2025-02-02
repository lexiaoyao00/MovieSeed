
from modules.spiders import PageParser,MultiLevelSpider,g_spider_logger
from urllib.parse import urljoin

ROOT_URL = "https://sukebei.nyaa.si/"


class ResultParser(PageParser):
    async def parse(self, soup, url):
        links = {}
        items = soup.select('table.torrent-list tbody tr')


        categories = []
        titles = []
        details_page = []
        torrents = []
        magnets = []
        size = []
        date = []
        seeders = []
        leechers = []
        downloads = []

        for item in items:
            categories.append(item.select_one('td:nth-child(1) a').attrs['title'])

            titles.append(item.select_one('td:nth-child(2) a:not([class])').get_text())
            details_page.append(ROOT_URL + item.select_one('td:nth-child(2) a').attrs['href'])


            seeds = item.select('td:nth-child(3) a')
            if len(seeds) == 1 and seeds[0].attrs['href'].startswith('magnet'):
                magnets.append(seeds[0].attrs['href'])
                torrents.append('-')
            elif len(seeds) == 2:
                torrents.append(ROOT_URL + item.select_one('td:nth-child(3) a:nth-child(1)').attrs['href'])
                magnets.append(item.select_one('td:nth-child(3) a:nth-child(2)').attrs['href'])
            else:
                g_spider_logger.warning(f'Can not parse seeds:{seeds}')
                torrents.append('-')
                magnets.append('-')


            size.append(item.select_one('td:nth-child(4)').get_text())

            date.append(item.select_one('td:nth-child(5)').get_text())

            seeders.append(item.select_one('td:nth-child(6)').get_text())

            leechers.append(item.select_one('td:nth-child(7)').get_text())

            downloads.append(item.select_one('td:nth-child(8)').get_text())



        # title_selects = soup.select('table.torrent-list tr td[colspan="2"] a:not([class])')
        # links['titles'] = [s['title'] for s in title_selects]
        links['categories'] = categories
        links['titles'] = titles
        links['details_page'] = details_page
        links['torrents'] = torrents
        links['magnets'] = magnets
        links['size'] = size
        links['date'] = date
        links['seeders'] = seeders
        links['leechers'] = leechers
        links['downloads'] = downloads
        return links

    def get_next_links(self, soup, url):
        links = []
        next_page_link = soup.select_one('li.next a')
        if next_page_link and next_page_link.has_attr('href'):
            links.append((urljoin(ROOT_URL,next_page_link['href']),False)) # 同级别网页

        next_depth_links = soup.select('table.torrent-list tr td[colspan="2"] a:not([class])')
        links.extend([(urljoin(ROOT_URL, link['href']),True) for link in next_depth_links])
        return links


class InfoParser(PageParser):
    async def parse(self, soup, url):
        titles  = soup.select_one('h3.panel-title')
        return {'titles':[titles.get_text()]}

    def get_next_links(self, soup, url):
        return []

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

        nyaa_parsers = {
            0: ResultParser(),
            # 1: InfoParser(),
        }

        spider = MultiLevelSpider(ROOT_URL, parsers=nyaa_parsers, max_depth=len(nyaa_parsers))
        results = spider.start(ROOT_URL,self.params)

        # print(results)
        spider.save_to_csv("results.csv")
        # for title in results[0]:
        #     print(title)
