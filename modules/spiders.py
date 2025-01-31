import asyncio
from curl_cffi import requests
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
# from urllib.parse import urljoin
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl
# import re
import platform
import pandas as pd
from collections import defaultdict

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
    def __init__(self, base_url, parsers, max_depth=3, delay=1, concurrency=5, impersonate=None):
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
        self.results = defaultdict(list)

        if impersonate:
            self.session = AsyncSession(impersonate=impersonate)
        else:
            self.session = AsyncSession()

    @staticmethod
    def set_event_loop_policy():
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    def build_url(self, url, params=None):
        if not params:
            return url

        parsed_url = urlparse(url)
        query_dict = dict(parse_qsl(parsed_url.query))
        query_dict.update(params)
        new_query = urlencode(query_dict)

        return urlunparse(
            (parsed_url.scheme, parsed_url.netloc, parsed_url.path,
             parsed_url.params, new_query, parsed_url.fragment)
        )

    async def get_page(self, url, params=None):
        full_url = self.build_url(url, params)
        try:
            async with self.semaphore:
                await asyncio.sleep(self.delay)
                response = await self.session.get(full_url, headers=self.headers)
                response.raise_for_status()
                return response.text
        except Exception as e:
            g_spider_logger.error(f"Error fetching {full_url}: {e}")
            return None

    def parse_page(self, html):
        return BeautifulSoup(html, 'html.parser')

    async def crawl_page(self, url, depth, params=None):
        full_url = self.build_url(url, params)
        if full_url in self.visited_urls or depth >= self.max_depth:
            return

        self.visited_urls.add(full_url)
        g_spider_logger.info(f"Crawling: {full_url} (Depth: {depth})")

        html = await self.get_page(url, params)
        if html:
            soup = self.parse_page(html)
            parser = self.parsers.get(depth)

            if parser:
                data = await parser.parse(soup, full_url)
                if data:
                    for key, values in data.items():
                        self.results[key].extend(values)

                next_links = parser.get_next_links(soup, full_url)
            else:
                next_links = []

            if depth < self.max_depth:
                tasks = []
                for link in next_links:
                    if isinstance(link, tuple):
                        next_url, next_params = link
                    else:
                        next_url, next_params = link, None

                    next_full_url = self.build_url(next_url, next_params)
                    if next_full_url not in self.visited_urls:
                        next_depth = parser.get_next_depth(depth)
                        task = asyncio.create_task(self.crawl_page(next_url, next_depth, next_params))
                        tasks.append(task)
                await asyncio.gather(*tasks)

    def get_series(self):
        """
        返回每个属性的 pandas Series
        """
        return {key: pd.Series(value) for key, value in self.results.items()}

    async def run(self, url=None, params=None):
        try:
            start_url = url or self.base_url
            await self.crawl_page(start_url, 0, params)
        finally:
            await self.session.close()
        return self.get_series()

    def start(self, url=None, params=None):
        self.set_event_loop_policy()
        return asyncio.run(self.run(url, params))

    def save_to_csv(self, filename):
        """
        将结果保存为 CSV 文件
        """
        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False)
        g_spider_logger.info(f"Results saved to {filename}")

    def save_to_excel(self, filename):
        """
        将结果保存为 Excel 文件
        """
        df = pd.DataFrame(self.results)
        df.to_excel(filename, index=False)
        g_spider_logger.info(f"Results saved to {filename}")
