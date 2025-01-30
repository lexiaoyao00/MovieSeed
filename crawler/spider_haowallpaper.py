
from modules.spiders import PageParser,MultiLevelSpider

class PostListParser(PageParser):
    async def parse(self, soup, url):
        # //*[@id="contentDiv"]/div/div/div[1]/div/div[1]/div[1]/div[2]/a
        print(f"url={url}")
        post_links = soup.select('div.card img')
        print(post_links)
        return [link['src'] for link in post_links]

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

        spider = MultiLevelSpider("https://haowallpaper.com/", parsers, max_depth=1)
        results = spider.start()

        print(results)

if __name__ == "__main__":
    sp = SPhaowallpaer()
    sp.crawl()