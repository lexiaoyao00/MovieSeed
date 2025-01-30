import asyncio
from curl_cffi import requests
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from urllib.parse import urljoin
import re
import platform
import logging
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PageParser(ABC):
    @abstractmethod
    async def parse(self, soup:BeautifulSoup, url):
        pass

    @abstractmethod
    def get_next_links(self, soup:BeautifulSoup, url):
        pass

    def get_next_depth(self, current_depth):
        # 默认行为是增加深度
        return current_depth + 1

class PostListParser(PageParser):
    async def parse(self, soup, url):
        # //*[@id="contentDiv"]/div/div/div[1]/div/div[1]/div[1]/div[2]/a
        print(f"url={url}")
        post_links = soup.select('a.post-preview-link')
        print(post_links)
        return [urljoin(url, link['href']) for link in post_links]

    def get_next_links(self, soup, url):
        return []

class PostDetailParser(PageParser):
    async def parse(self, soup, url):
        logger.debug('PostDetailParser test')
        return []

    def get_next_links(self, soup, url):
        return []

class PostPageParser(PageParser):
    async def parse(self, soup, url):
        logger.debug('PostPageParser test')
        return None

    def get_next_links(self, soup, url):
        return None

    def get_next_depth(self, current_depth):
        return current_depth

class MultiLevelSpider(ABC):
    def __init__(self, base_url, parsers, max_depth=3, delay=1, concurrency=5,impersonate=None):
        self.base_url = base_url
        self.parsers = parsers
        self.max_depth = max_depth
        self.delay = delay
        self.concurrency = concurrency
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
        }

        self.visited_urls = set()
        self.semaphore = asyncio.Semaphore(concurrency)
        self.results = []

        if impersonate:
            self.session = AsyncSession(impersonate=impersonate)
        else:
            self.session = AsyncSession()


    @staticmethod
    def set_event_loop_policy():
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    async def get_page(self, url):
        try:
            async with self.semaphore:
                await asyncio.sleep(self.delay)
                response = await self.session.get(url, headers=self.headers)
                response.raise_for_status()
                return response.text
        except requests.RequestsError as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    # async def get_page(self, url):
    #     try:
    #         async with self.semaphore:
    #             await asyncio.sleep(self.delay)

    #             # 使用 Playwright 获取渲染后的内容
    #             async with async_playwright() as p:
    #                 browser = await p.chromium.launch()
    #                 page = await browser.new_page()
    #                 await page.goto(url)
    #                 content = await page.content()
    #                 await browser.close()
    #                 return content

    #     except Exception as e:
    #         logger.error(f"Error fetching {url}: {e}")
    #         return None

    def parse_page(self, html):
        return BeautifulSoup(html, 'html.parser')

    async def crawl_page(self, url, depth):
        if url in self.visited_urls or depth >= self.max_depth:
            return

        self.visited_urls.add(url)
        logger.info(f"Crawling: {url} (Depth: {depth})")

        html = await self.get_page(url)
        if html:
            soup = self.parse_page(html)
            parser = self.parsers.get(depth)

            if parser:
                data = await parser.parse(soup, url)
                if data:
                    self.results.append(data)
                next_links = parser.get_next_links(soup, url)
            else:
                next_links = []

            if depth < self.max_depth:
                tasks = []
                for link in next_links:
                    if link not in self.visited_urls:
                        next_depth = parser.get_next_depth(depth)
                        task = asyncio.create_task(self.crawl_page(link, next_depth))
                        tasks.append(task)
                await asyncio.gather(*tasks)

    async def run(self):
        try:
            await self.crawl_page(self.base_url, 0)
        finally:
            await self.session.close()
        return self.results

    def start(self):
        self.set_event_loop_policy()
        return asyncio.run(self.run())

# 使用示例
if __name__ == "__main__":
    parsers = {
        0: PostListParser(),
        1: PostDetailParser(),
        2: PostPageParser(),
    }

    spider = MultiLevelSpider("https://danbooru.donmai.us/", parsers, max_depth=1)
    results = spider.start()

    print(results)
    # 处理结果
    # post_details = {}
    # for result in results:
    #     if result['type'] == 'post_detail':
    #         post_details[result['url']] = {
    #             'title': result['data']['title'],
    #             'description': result['data']['description'],
    #             'images': []
    #         }
    #     elif result['type'] == 'post_page':
    #         post_url = '/'.join(result['url'].split('/')[:-1])  # 移除 '/pageX' 部分
    #         if post_url in post_details:
    #             post_details[post_url]['images'].append(result['data']['img_url'])

    # # 打印结果
    # for post_url, post_data in post_details.items():
    #     print(f"Post URL: {post_url}")
    #     print(f"Title: {post_data['title']}")
    #     print(f"Description: {post_data['description']}")
    #     print(f"Number of images: {len(post_data['images'])}")
    #     print("Image URLs:")
    #     for img_url in post_data['images']:
    #         print(f"  - {img_url}")
    #     print()
