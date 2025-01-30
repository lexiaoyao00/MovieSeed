import asyncio
from curl_cffi import requests
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
# from urllib.parse import urljoin
# import re
import platform

from common.logger import g_spider_logger

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
            g_spider_logger.error(f"Error fetching {url}: {e}")
            return None

    def parse_page(self, html):
        return BeautifulSoup(html, 'html.parser')

    async def crawl_page(self, url, depth):
        if url in self.visited_urls or depth >= self.max_depth:
            return

        self.visited_urls.add(url)
        g_spider_logger.info(f"Crawling: {url} (Depth: {depth})")

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

