
from modules.spiders import PageParser,MultiLevelSpider

ROOT_URL = "https://haowallpaper.com/"

class PostListParser(PageParser):
    async def parse(self, soup, url):
        post_links = soup.select('div.card img')
        return {'posts':[link['src'] for link in post_links]}

    def get_next_links(self, soup, url):
        return []

    def get_next_depth(self, current_depth):
        return current_depth

class SPhaowallpaer:
    def __init__(self):
        pass

    def crawl(self):

        parsers = {
            0: PostListParser(),
        }

        spider = MultiLevelSpider(ROOT_URL, parsers, max_depth=1)
        results = spider.start()

        print(results)

if __name__ == "__main__":
    sp = SPhaowallpaer()
    sp.crawl()